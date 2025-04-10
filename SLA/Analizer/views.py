from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Subject,CustomUser,QuestionPaper, Chat, ChatMessage,Question
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import pytesseract
from pdf2image import convert_from_bytes
import re
import os
import tempfile
import shutil
import base64
from google import genai
from google.genai import types
import mimetypes


# Create your views here.

def dashboard(request):
    question_papers = QuestionPaper.objects.all().order_by('-year', '-semester')
    return render(request,'dashboard.html',{'question_papers':question_papers})
    

def User_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request,email=email,password=password)
        if user is not None:
            login(request,user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request,'login.html')

def User_register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        mobile_no = request.POST['mobile_no']
        password = request.POST['password1']
        user = CustomUser.objects.create_user(email=email,password=password,first_name=first_name,last_name=last_name,mobile_no=mobile_no)
        return redirect('login')
    return render(request,'register.html')

@login_required(login_url='login')
def add_subject(request):
    if request.method == 'POST':
        subject_name=request.POST['name']
        subject_code=request.POST['code']
        subject_description=request.POST['description']
        semister=request.POST['semister']
        subject=Subject(name=subject_name,code=subject_code,description=subject_description,semister=semister)
        subject.save()
        return redirect('dashboard')
    return render(request,'add_subject.html')

@login_required(login_url='login')
def subject_info(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    question_papers = QuestionPaper.objects.filter(subject=subject).order_by('-year', '-semester')
    return render(request, 'subject_info.html', {
        'subject': subject,
        'question_papers': question_papers
    })

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return redirect('login')

def extract_questions_from_text(text):
    text = re.sub(r"GOVERNMENT POLYTECHNIC.*?Instruction :-", "", text, flags=re.DOTALL)
    text = re.sub(r"EXAMSEATNO.*?DATE.*?\n", "", text)
    text = re.sub(r"Q\d+\]?\s*\|?\s*Attempt.*?\n", "", text)

    text = text.replace('—', '-').replace('=', '-').replace('|', '')
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    question_patterns = [
        r"^(?:[a-z]\)|[a-z]\.)\s", r"^(?:[ivxlcdm]+\))\s", r"^Q\d+\.\s",
        r"^(?:[0-9]+\))\s", r"^(Define|Explain|Distinguish|Draw|Compare|List|State|Write|Find|Consider|Determine)\b",
    ]
    question_regex = re.compile("|".join(question_patterns), re.IGNORECASE)

    questions = []
    buffer = ""

    for line in lines:
        if question_regex.match(line):
            if buffer:
                questions.append(buffer.strip())
                buffer = ""
            buffer = line
        else:
            buffer += " " + line

    if buffer:
        questions.append(buffer.strip())

    return questions

def extract_text_from_image_pdf(pdf_file):
    try:
        # Check if Tesseract is installed
        if not os.path.exists(r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
            raise Exception("Tesseract is not installed. Please install it from https://github.com/UB-Mannheim/tesseract/wiki")
            
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save the uploaded file temporarily
            temp_pdf_path = os.path.join(temp_dir, 'temp.pdf')
            with open(temp_pdf_path, 'wb') as temp_file:
                for chunk in pdf_file.chunks():
                    temp_file.write(chunk)
            
            try:
                # Convert PDF to images using the temporary file
                images = convert_from_bytes(open(temp_pdf_path, 'rb').read())
            except Exception as e:
                if "poppler" in str(e).lower():
                    raise Exception(
                        "Poppler is not installed or not in PATH. Please:\n"
                        "1. Download from: https://github.com/oschwartz10612/poppler-windows/releases/\n"
                        "2. Extract to C:\\Program Files\\poppler\n"
                        "3. Add C:\\Program Files\\poppler\\Library\\bin to your system PATH\n"
                        "4. Restart your Django server"
                    )
                raise e

            full_text = ""
            for img in images:
                text = pytesseract.image_to_string(img)
                full_text += text + "\n"

            extracted_questions = extract_questions_from_text(full_text)
            return extracted_questions
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return []

@login_required(login_url='login')
def upload_question_paper(request, subject_id):
    if request.method == 'POST':
        subject = Subject.objects.get(id=subject_id)
        title = request.POST.get('title')
        year = request.POST.get('year')
        semester = request.POST.get('semester')
        pdf_file = request.FILES.get('pdf_file')
        
        if pdf_file and pdf_file.content_type != 'application/pdf':
            messages.error(request, 'Please upload a PDF file.')
            return redirect('subject_info', subject_id=subject_id)
            
        paper = QuestionPaper.objects.create(
            subject=subject,
            title=title,
            year=year,
            semester=semester,
            pdf_file=pdf_file
        )
        
        # Extract questions from the uploaded PDF file
        try:
            text_output = extract_text_from_image_pdf(pdf_file)
            if text_output:
                for question in text_output:
                    Question.objects.create(
                        question=question,
                        question_paper=paper,
                        question_type='extracted'  # Default type for extracted questions
                    )
                    print(question)
            else:
                messages.warning(request, "No questions were extracted from the PDF.")
        except Exception as e:
            messages.error(request, f"Error processing PDF: {str(e)}")
            return redirect('subject_info', subject_id=subject_id)

        messages.success(request, 'Question paper uploaded successfully.')
        return redirect('subject_info', subject_id=subject_id)
    
    return redirect('subject_info', subject_id=subject_id)

def suubb(request):
    return render(request,"sub_info.html")

@login_required(login_url='login')
def subjects(request):
    subjects = Subject.objects.all()
    return render(request, 'subjects.html', {'subjects': subjects})

@login_required(login_url='login')
def chat_view(request):
    # Get all chats for the current user, ordered by most recent first
    chats = Chat.objects.filter(user=request.user).order_by('-updated_at')
    
    # Get current chat ID from query params or use the most recent chat
    current_chat_id = request.GET.get('chat_id')
    if not current_chat_id and chats.exists():
        current_chat_id = chats.first().id
    
    # Get messages for the current chat if it exists
    current_chat_messages = []
    if current_chat_id:
        try:
            current_chat = Chat.objects.get(id=current_chat_id, user=request.user)
            current_chat_messages = ChatMessage.objects.filter(chat=current_chat).order_by('created_at')
        except Chat.DoesNotExist:
            current_chat_id = None
    
    context = {
        'chats': chats,
        'current_chat_id': current_chat_id,
        'current_chat_messages': current_chat_messages,
    }
    
    return render(request, 'Analizer/chat.html', context)

@login_required(login_url='login')
@require_POST
def start_chat(request):
    chat = Chat.objects.create(user=request.user)
    return JsonResponse({'chat_id': chat.id})

def generate(msg, chat_history=None):
    client = genai.Client(
        api_key="AIzaSyCfnn4Q3bAA2AON_b8AUjd5UfYtl075duo",
    )

    # Prepare context from chat history
    context = ""
    if chat_history:
        for message in chat_history:
            role = "Assistant" if message.is_bot else "User"
            context += f"{message.content}\n"

    # Combine context with current message
    full_prompt = f"Previous conversation:\n{context}\nCurrent message: {msg}"

    model = "gemini-2.0-flash-exp-image-generation"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=full_prompt),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_modalities=["text"],
        response_mime_type="text/plain",
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if not chunk.candidates or not chunk.candidates[0].content or not chunk.candidates[0].content.parts:
            continue
        if not chunk.candidates[0].content.parts[0].inline_data:
            response_text += chunk.text

    return response_text


@login_required(login_url='login')
@require_POST
def send_message(request):
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        message = data.get('message')
        
        if not chat_id or not message:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing chat_id or message'
            }, status=400)
        
        chat = Chat.objects.get(id=chat_id, user=request.user)
        
        # Save user message
        user_message = ChatMessage.objects.create(
            chat=chat,
            content=message,
            is_bot=False
        )
        print(user_message)

        # Get chat history for context
        chat_history = ChatMessage.objects.filter(chat=chat).order_by('created_at')[:5]  # Last 5 messages for context
        
        # Generate bot response with context
        bot_response = generate(message, chat_history)
        
        # Update chat's last update time
        chat.save()  # This will update the updated_at field
        
        # Save bot response
        bot_message = ChatMessage.objects.create(
            chat=chat,
            content=bot_response,
            is_bot=True
        )
        
        return JsonResponse({
            'status': 'success',
            'bot_response': bot_response,
            'timestamp': bot_message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    except Chat.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Chat not found'
        }, status=404)
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

@login_required(login_url='login')
@require_POST
def get_chat_messages(request):
    data = json.loads(request.body)
    chat_id = data.get('chat_id')
    
    try:
        chat = Chat.objects.get(id=chat_id, user=request.user)
        messages = ChatMessage.objects.filter(chat=chat).order_by('created_at')
        
        messages_data = [{
            'content': msg.content,
            'is_bot': msg.is_bot,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for msg in messages]
        
        return JsonResponse({
            'status': 'success',
            'messages': messages_data
        })
    except Chat.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Chat not found'
        }, status=404)
