from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

def home(request):
    return render(request, 'agriai/home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'agriai/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'agriai/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    return render(request, 'agriai/dashboard.html')



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .utils import predictor

@login_required
def plant_analysis(request):
    context = {}
    
    if request.method == 'POST':
        # Handle image upload
        if 'plant_image' in request.FILES:
            uploaded_file = request.FILES['plant_image']
            file_result = predictor.handle_uploaded_file(uploaded_file)
            
            if file_result['success']:
                analysis_result = predictor.analyze_plant_image(file_result['file_path'])
                predictor.cleanup_file(file_result['file_path'])
                
                if analysis_result['success']:
                    request.session['symptoms'] = analysis_result['analysis']
                    context.update({
                        'analysis': analysis_result['analysis'],
                        'show_research': True
                    })
                else:
                    context['error'] = analysis_result['error']
            else:
                context['error'] = file_result['error']
        
        # Handle manual symptom submission
        elif 'symptoms' in request.POST:
            symptoms = request.POST.get('symptoms')
            research_result = predictor.research_disease(symptoms)
            
            if research_result['success']:
                context['research'] = research_result['research']
            else:
                context['error'] = research_result['error']
    
    return render(request, 'agriai/plant_analysis.html', context)