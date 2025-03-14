from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import App, UserPurchase
import os
import subprocess
import random
import string
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from base64 import b64encode
import json
import requests
import time
from urllib.parse import urlparse
import hashlib
from xml.etree import ElementTree as ET
from django.contrib.auth.decorators import login_required

# Helper Functions for WeChat Pay
def generate_nonce_str(length=32):
    """Generate a random nonce string for WeChat Pay API requests."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def generate_sign(params, api_key):
    """Generate a signature for WeChat Pay API requests."""
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    string_to_sign = '&'.join([f"{key}={value}" for key, value in sorted_params]) + f"&key={api_key}"
    return hashlib.md5(string_to_sign.encode('utf-8')).hexdigest().upper()

# Views
def index(request):
    """Display a random selection of 6 apps on the homepage."""
    apps = App.objects.order_by('?')[:6]
    return render(request, 'user/index.html', {'apps': apps, 'MEDIA_URL': settings.MEDIA_URL})

def applist(request, category=None):
    """List all apps, optionally filtered by category."""
    categories = App.objects.values_list('category', flat=True).distinct()
    if category:
        apps = App.objects.filter(category=category)
    else:
        apps = App.objects.all()
    return render(request, 'user/applist.html', {
        'apps': apps,
        'categories': categories,
        'selected_category': category,
        'MEDIA_URL': settings.MEDIA_URL
    })

@login_required
def app_detail(request, app_name):
    """Display detailed information about a specific app."""
    app = get_object_or_404(App, name=app_name)
    host_url = request.scheme + '://' + request.get_host()
    purchased = UserPurchase.objects.filter(user=request.user, app=app, status='completed').exists()
    if request.is_secure():
        host_url = host_url.replace("http://", "https://")
    else:
        host_url = host_url.replace("http://", "https://")
    apps = App.objects.order_by('?')[:5]  # Related apps
    screenshots_folder = os.path.join('media', 'screenshots', app_name)
    screenshots = [os.path.join('screenshots', app_name, file) for file in os.listdir(screenshots_folder)
                   if file.endswith(('png', 'jpg', 'jpeg', 'gif'))] if os.path.exists(screenshots_folder) else []
    return render(request, 'user/app_detail.html', {
        'app': app,
        'apps': apps,
        'screenshots': screenshots,
        'MEDIA_URL': settings.MEDIA_URL,
        'host_url': host_url,
        'purchased': purchased
    })

def search_app(request):
    """Search for an app by name and redirect to its detail page."""
    query = request.GET.get('query')
    app = App.objects.filter(name__icontains=query).first()
    if app:
        return redirect('app_detail', app_name=app.name)
    messages.error(request, 'App not found')
    return redirect('index')

def install_app_route(request, app_name):
    """Handle the installation of an app."""
    app = get_object_or_404(App, name=app_name)
    install_app(app)
    messages.success(request, f'Installing {app_name}...')
    return redirect('index')

def install_app(app):
    """Execute the app's installation script."""
    if app.script:
        subprocess.Popen(['cmd', '/c', 'start', app.script])

@login_required
def payment_view(request, app_id):
    """Initiate a WeChat Pay payment and return a QR code URL and transaction ID."""
    app = get_object_or_404(App, id=app_id)
    user = request.user
    if UserPurchase.objects.filter(user=user, app=app, status='completed').exists():
        return JsonResponse({'error': 'Already purchased'}, status=400)

    # Generate a unique transaction ID
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    # Load RSA key for signing (update path to your key file)
    try:
        rsa_key = RSA.importKey(open(settings.KEY_PATH).read())
    except Exception as e:
        return JsonResponse({'error': 'Payment configuration error'}, status=500)

    total_amount = int(float(app.price) * 100)  # Convert price to cents
    data = {
        "mchid": settings.MCH_ID,  # Your WeChat merchant ID
        "out_trade_no": random_string,
        "appid": settings.APP_ID,  # Your WeChat app ID
        "description": f'Purchase: {app.name}',
        "notify_url": f'{request.build_absolute_uri("/")}payment/notify/',
        "amount": {
            "total": total_amount,
            "currency": "CNY"
        }
    }

    try:
        json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
    except TypeError as e:
        return JsonResponse({'error': f'JSON error: {str(e)}'}, status=500)

    # Generate signature for WeChat Pay API
    request_random_str = generate_nonce_str()
    timestamp = str(int(time.time()))
    payment_url = 'https://api.mch.weixin.qq.com/v3/pay/transactions/native'
    sign_str = '\n'.join([
        "POST",
        urlparse(payment_url).path,
        timestamp,
        request_random_str,
        json_data.decode('utf-8'),
        ''
    ])
    signer = pkcs1_15.new(rsa_key)
    digest = SHA256.new(sign_str.encode('utf8'))
    signature = b64encode(signer.sign(digest)).decode('utf-8')

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'WECHATPAY2-SHA256-RSA2048 mchid="1652956134",nonce_str="{request_random_str}",signature="{signature}",timestamp="{timestamp}",serial_no="367355315941CFD81E135CD5321161EBB233F8A5"'
    }

    try:
        response = requests.post(payment_url, data=json_data, headers=headers)
        response.raise_for_status()
        result = response.json()
        if 'code_url' not in result:
            return JsonResponse({'error': 'WeChat API error: ' + str(result)}, status=500)

        # Create a pending purchase record
        UserPurchase.objects.create(
            user=user,
            app=app,
            transaction_id=random_string,
            status='pending'
        )

        # Return both qr_code_url and transaction_id
        return JsonResponse({
            'qr_code_url': result['code_url'],
            'transaction_id': random_string
        })

    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Payment failed: {str(e)}'}, status=500)

@csrf_exempt
def payment_notify(request):
    """Handle WeChat Pay notification to update purchase status."""
    if request.method != 'POST':
        return HttpResponse(status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
        transaction_id = body.get('out_trade_no')
        if not transaction_id:
            return HttpResponse(status=400)

        purchase = UserPurchase.objects.get(transaction_id=transaction_id)
        purchase.status = 'completed'
        purchase.save()
        return HttpResponse(status=200)
    except UserPurchase.DoesNotExist:
        return HttpResponse(status=404)
    except Exception as e:
        print(f"Payment notification error: {str(e)}")
        return HttpResponse(status=500)

def check_payment_status(request, transaction_id):
    """Check the payment status and update the database."""
    try:
        purchase = UserPurchase.objects.get(transaction_id=transaction_id)
        if purchase.status == 'completed':
            return JsonResponse({'status': 'success'})

        # WeChat Pay credentials
        appid = settings.APP_ID
        mch_id = settings.MCH_ID
        api_key = settings.API_KEY  # Your API key
        nonce_str = generate_nonce_str()

        params = {
            "appid": appid,
            "mch_id": mch_id,
            "out_trade_no": transaction_id,
            "nonce_str": nonce_str
        }
        sign = generate_sign(params, api_key)
        params['sign'] = sign

        # Construct XML for order query
        xml_data = "<xml>"
        for key, value in params.items():
            xml_data += f"<{key}>{value}</{key}>"
        xml_data += "</xml>"

        url = "https://api.mch.weixin.qq.com/pay/orderquery"
        headers = {'Content-Type': 'application/xml'}
        response = requests.post(url, data=xml_data.encode('utf-8'), headers=headers)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            result = {elem.tag: elem.text for elem in root}
            if result.get('trade_state') == 'SUCCESS':
                purchase.status = 'completed'
                purchase.save()
                return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'pending'})
    except UserPurchase.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)