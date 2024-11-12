from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import App
from django.core.files.storage import default_storage
import os, subprocess, zipfile, re, shutil
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify
from .forms import LoginForm, UserRegistrationForm, UserProfileForm
from django.http import HttpResponseForbidden

# Create your views here.
def index(request):
    apps = App.objects.order_by('?')[:6]
    return render(request, 'user/index.html', {'apps': apps, 'MEDIA_URL': settings.MEDIA_URL})

@login_required
def applist(request, category=None):
    # Fetch all categories for sidebar
    categories = App.objects.values_list('category', flat=True).distinct()
    
    # Filter apps based on selected category, if any
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
    app = get_object_or_404(App, name=app_name)
    host_url = request.scheme + '://' + request.get_host()
    apps = App.objects.order_by('?')[:5]
    screenshots_folder = os.path.join('media', 'screenshots', app_name)
    screenshots = [os.path.join('screenshots', app_name, file) for file in os.listdir(screenshots_folder)
                   if file.endswith(('png', 'jpg', 'jpeg', 'gif'))] if os.path.exists(screenshots_folder) else []
    return render(request, 'user/app_detail.html', {'app': app, 'apps': apps, 'screenshots': screenshots, 'MEDIA_URL': settings.MEDIA_URL, 'host_url': host_url})

@login_required
def search_app(request):
    query = request.GET.get('query')
    app = App.objects.filter(name__icontains=query).first()
    if app:
        return redirect('app_detail', app_name=app.name)
    messages.error(request, 'App not found')
    return redirect('index')

@login_required
def install_app_route(request, app_name):
    app = get_object_or_404(App, name=app_name)
    install_app(app)
    messages.success(request, f'Installing {app_name}...')
    return redirect('index')

@login_required
def install_app(app):
    if app.script:
        subprocess.Popen(['cmd', '/c', 'start', app.script])

#======================================Admin Panel===============================================================

def login_view(request):
    if request.user.is_authenticated:
        # Redirect based on user staff status
        if request.user.is_staff:
            return redirect('admin_page')
        else:
            return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')

                # Check if the user is a staff member
                if user.is_staff:
                    return redirect('admin_page')  # Redirect staff to admin page
                else:
                    return redirect('index')  # Redirect non-staff users to the main index page
            else:
                messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()

    return render(request, 'managers/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

@login_required
def admin_page(request, category=None):
    if not request.user.is_staff:
        return HttpResponseForbidden("back to admin page")

    categories = App.objects.values_list('category', flat=True).distinct()

        # Filter apps based on selected category, if any
    if category:
        apps = App.objects.filter(category=category)
    else:
        apps = App.objects.all()
    return render(request, 'managers/index.html', {'apps': apps, 'MEDIA_URL': settings.MEDIA_URL, 'categories': categories, 'selected_category': category,} )

@login_required
def add_app(request):
    script_files = ''  # Initialize script_files to an empty list
    zip_path = request.POST.get('zip_path', '')
    unzip_path = request.POST.get('unzip_path', '')

    if request.method == 'POST':
        # Step 1: Handle zip file upload
        zip_file = request.FILES.get('zipfile')
        if zip_file:
            if not zip_file.name.endswith('.zip'):
                messages.error(request, "Invalid or missing zip file!")
                return redirect('add_app')

            # Save and extract the zip file
            zip_path = default_storage.save(os.path.join('zip', zip_file.name), zip_file)
            unzip_path = os.path.join(settings.MEDIA_ROOT, 'unzipped', zip_file.name[:-4])
            os.makedirs(unzip_path, exist_ok=True)

            with zipfile.ZipFile(os.path.join(settings.MEDIA_ROOT, zip_path), 'r') as zip_ref:
                zip_ref.extractall(unzip_path)

            # List .exe and .bat files
            script_files = [f for f in os.listdir(unzip_path) if f.endswith(('.exe', '.bat'))]
            if not script_files:
                messages.error(request, "No valid script files found in the zip!")
                return redirect('add_app')

            # Render the form with the script files and unzip folder
            return render(request, 'managers/add_app.html', {
                'files': script_files,
                'unzip_path': unzip_path,
                'zip_path': zip_path,
            })

        # Step 2: Handle the main form submission
        name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        selected_script = request.POST.get('selected_file')

        if name and description and category and selected_script:
            try:
                with transaction.atomic():
                    # Save the app instance
                    app = App(
                        name=name,
                        description=description,
                        category=category,
                        zip_path=zip_path,
                        unzip_path=unzip_path,
                        script=os.path.join(unzip_path, selected_script),
                    )

                    # Handle icon upload
                    icon_file = request.FILES.get('icon_path')
                    if icon_file:
                        app.icon_path = default_storage.save(os.path.join('icons', icon_file.name), icon_file)

                    # Save screenshots
                    screenshots = request.FILES.getlist('screenshots')
                    screenshot_dir = os.path.join('screenshots', name)
                    os.makedirs(os.path.join(settings.MEDIA_ROOT, screenshot_dir), exist_ok=True)
                    for file in screenshots:
                        if file:
                            default_storage.save(os.path.join(screenshot_dir, file.name), file)

                    app.save()

                    messages.success(request, 'App successfully added!')
                    return redirect('admin_page')
            except Exception as e:
                messages.error(request, f"An error occurred while saving the app: {e}")
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'managers/add_app.html', {'files': script_files, 'zip_path': zip_path})

@login_required
def edit_app(request, id):
    app_record = get_object_or_404(App, id=id)

    if request.method == 'POST':
        new_name = request.POST.get('name')
        description = request.POST.get('description')
        category = request.POST.get('category')
        icon_file = request.FILES.get('icon_file')  # New icon (optional)
        files = request.FILES.getlist('screenshots')  # New screenshots (optional)

        if not new_name:
            messages.error(request, 'Name is required!')
            return redirect(reverse('edit_app', args=[id]))

        # Handle icon update
        if icon_file and icon_file.name.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            icon_filename = slugify(icon_file.name)
            new_icon_path = f'icons/{icon_filename}'

            # Save the new icon file
            full_new_icon_path = os.path.join(settings.MEDIA_ROOT, new_icon_path)
            with default_storage.open(full_new_icon_path, 'wb+') as destination:
                for chunk in icon_file.chunks():
                    destination.write(chunk)

            # Remove the old icon file if it exists
            old_icon_path = app_record.icon_path
            if old_icon_path and default_storage.exists(os.path.join(settings.MEDIA_ROOT, old_icon_path)):
                try:
                    default_storage.delete(os.path.join(settings.MEDIA_ROOT, old_icon_path))
                except Exception as e:
                    messages.warning(request, f"Error deleting old icon: {e}")
        else:
            # No new icon uploaded, use the old path
            new_icon_path = app_record.icon_path

        # Handle app name change: rename screenshots folder if needed
        old_app_folder_name = slugify(app_record.name)
        new_app_folder_name = slugify(new_name)
        old_app_folder = os.path.join(settings.MEDIA_ROOT, 'screenshots', old_app_folder_name)
        new_app_folder = os.path.join(settings.MEDIA_ROOT, 'screenshots', new_app_folder_name)

        if old_app_folder_name != new_app_folder_name:
            if os.path.exists(old_app_folder):
                os.rename(old_app_folder, new_app_folder)
            else:
                os.makedirs(new_app_folder, exist_ok=True)
        else:
            new_app_folder = old_app_folder

        # Save new screenshots
        for file in files:
            if file.name.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                filename = slugify(file.name)
                with default_storage.open(os.path.join(new_app_folder, filename), 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

        # Update the app record in the database
        app_record.name = new_name
        app_record.description = description
        app_record.category = category
        app_record.icon_path = new_icon_path

        try:
            app_record.save()
            messages.success(request, 'App successfully updated!')
        except Exception:
            messages.error(request, 'App name already exists. Choose a different name.')
            # Optionally, remove the new icon if DB update fails
            if icon_file and default_storage.exists(full_new_icon_path):
                default_storage.delete(full_new_icon_path)
            return redirect(reverse('edit_app', args=[id]))

        return redirect('admin_page')

    return render(request, 'managers/edit_app.html', {'app': app_record, 'MEDIA_URL': settings.MEDIA_URL})

def custom_secure_filename(name):
    return re.sub(r'[^\w\s.-]', '', name).strip()

@login_required
def delete_app(request, id):
    if request.method == 'POST':
        # Retrieve the app record, or return a 404 error if not found
        app_record = get_object_or_404(App, id=id)

        # Delete screenshots folder
        app_folder_name = custom_secure_filename(app_record.name)
        app_folder = os.path.join(settings.MEDIA_ROOT,'screenshots', app_folder_name)
        print(app_folder)
        if os.path.exists(app_folder):
            shutil.rmtree(app_folder)  # Deletes the folder and all its contents

        # Delete icon file
        icon_path = app_record.icon_path

        # Use the .path attribute to get the file's full path
        if icon_path:
            full_icon_path = icon_path.path  # This gives you the full path to the icon file
            if os.path.exists(full_icon_path):
                os.remove(full_icon_path)

        # Delete zip file
        zip_path = app_record.zip_path
        if zip_path:
            full_zip_path = zip_path.path  # Get the full file path
            if os.path.exists(full_zip_path):
                os.remove(full_zip_path)

        # Delete the script folder if exists
        folder_path = os.path.dirname(app_record.script)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        # Delete app from the database
        app_record.delete()
        messages.success(request, 'App successfully deleted!')
        return redirect('admin_page')  # Replace with your admin index URL name
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('admin_page')

#================================================Registeration===================================

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()

            messages.success(request, 'Your account has been created! You can now log in.')
            login(request, user)  # Automatically log in the user after registration
            return redirect('index')  # Redirect to main page
    else:
        user_form = UserRegistrationForm()
        profile_form = UserProfileForm()

    return render(request, 'managers/register.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def profile(request):
    profile = request.user.profile
    return render(request, 'user/profile.html', {'profile': profile,'MEDIA_URL': settings.MEDIA_URL})