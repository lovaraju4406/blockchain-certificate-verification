from datetime import timezone
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib import messages
import requests
from .logic import *
import datetime
from django.utils import timezone
from .models import CertificateRequest


# Create your views here.
def register_view(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        confirmpassword = request.POST.get('confirmpassword', '')
        
        
        if not username or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect('index')
        
        if password != confirmpassword:
            messages.error(request, "Passwords do not match!")
            return redirect('index')
        
        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters.")
            return redirect('index')
        
        try:
            data = retrieveData()
            if not isinstance(data, list):
                raise Exception(data)
        except Exception as e:
            print("Blockchain retrieve error:", e)
            messages.error(request, "Unable to fetch registration data. Try later.")
            return redirect('index')
        
        for record in data:
            if record.get('email') == email:
                messages.error(request, "This email is already registered.")
                return redirect('index')
        
        # Generate Registration ID 
        now = datetime.datetime.now()
        current_prefix = now.strftime("%Y%m")
        
        count_this_month = 0
        for record in data:
            if record.get('type') == 'Registration':
                try:
                    ts_str = record.get('timestamp', '')
                    if ts_str:
                        if 'T' in ts_str:
                            record_date = datetime.datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
                        else:
                            record_date = datetime.datetime.strptime(ts_str[:19], "%Y-%m-%d %H:%M:%S")
                        record_prefix = record_date.strftime("%Y%m")
                        if record_prefix == current_prefix:
                            count_this_month += 1
                except Exception as e:
                    print(f"Error parsing timestamp {ts_str}: {e}")
                    pass
        
        next_num = count_this_month + 1
        reg_id = f"{current_prefix}{next_num:03d}"
        
        try:
            user_data = {
                'type': 'Registration',
                'name': username,
                'email': email,
                'password': password,
                'status': False, 
                'timestamp': str(datetime.datetime.now()), 
                'reg_id': reg_id
            }
            
            result = addNewData(user_data)
            
            print("Blockchain response:", result)
            
            block_chain = retrieveData()
            print(block_chain, 'jkdjflkjaslkjfd')
            
            if "Success" not in result:
                raise Exception(result)
            
            messages.success(request, f"Account created successfully. Your Registration ID: {reg_id}. Please log in.")
            
            request.session['last_reg_id'] = reg_id
            request.session['last_email'] = email
            
            return redirect('index')
        
        except Exception as e:
            print("Blockchain add error:", e)
            messages.error(request, f"Failed to save data on blockchain: {str(e)}")
            return redirect('index')
        
    return render(request, 'index.html')


def login_view(request):
    if request.method == "POST":
        password = request.POST.get('password', '').strip()
        
        # Check Admin Login First
        email_input = request.POST.get('email', '').strip()
        if email_input and email_input == "admin@gmail.com" and password == "123456789":
            request.session['email'] = email_input
            request.session['data'] = {          # Recommended: match your template
                'name': "Admin",
                'role': "admin"
            }
            messages.success(request, "Admin login successful!")
            return redirect('admin_dashboard')  # ← CRITICAL: RETURN HERE!

        # Only proceed to user login if not admin
        reg_id = request.POST.get('reg_id', '').strip()
        
        if not reg_id or not password:
            messages.error(request, "Registration ID and password are required.")
            return redirect('index')
        
        try:
            data = retrieveData()
            user_found = None
            for user in data:
                if user.get('type') == 'Registration':
                    if user.get('reg_id') == reg_id and user.get('status') == True:
                        if user.get('password') == password:
                            user_found = user
                            break
                        
            if not user_found:
                messages.error(request, "Invalid credentials or account not approved.")
                return redirect('index')
            print('user', user_found)
            print('data', data)
            # User login success
            request.session['reg_id'] = reg_id
            request.session['u'] = user_found  # Store full user data
            messages.success(request, f"Welcome back, {user_found['name']}!")
            return redirect('user_dashboard')
        
        except Exception as e:
            print("Login error:", e)
            messages.error(request, "Login failed. Please try again later.")
            return redirect('index')
    
    return render(request, 'index.html')


def logout_view(request):
    request.session.flush()
    return redirect('index')

# def admin_dashboard(request):
#     if request.session.get('data')['role'] != 'admin':
#         messages.error(request, "Access denied. Admin login required.")
#         return redirect('index')
    
#     context = {
#         'total_users': 0,
#         'pending_requests': 0,
#         'verified_certificates': 0,
#         'rejected_requests': 0,
#         'today_registrations': 0,
#         'total_certificates': 0,
#         'recent_activities': []
#     }
    
#     try:
#         print("Fetching data from blockchain...")
#         all_data = retrieveData()
        
#         if not isinstance(all_data, list):
#             print("Warning: retrieveData() did not return a list:", all_data)
#             all_data = []
            
#         print(f"Retrieved {len(all_data)} records from blockchain.")
        
#         users = [
#             item for item in all_data
#             if item.get('type') == 'Registration' and item.get('status') == True
#         ]
        
#         certificate_requests = [
#             item for item in all_data
#             if item.get('type') in ['CertificateRequest', 'certificate_requested', 'CertRequest']
#         ]
        
#         pending_requests = [r for r in certificate_requests if r.get('status') == 'pending']
#         verified_certificates = [r for r in certificate_requests if r.get('status') == 'verified']
#         rejected_requests = [r for r in certificate_requests if r.get('status') == 'rejected']
        
#         total_certificates = len(verified_certificates)
        
#         today = timezone.now().date()
#         today_registrations = 0
#         for user in users:
#             ts = user.get('timestamp', '')
#             if not ts:
#                 continue
#             try:
                
#                 if isinstance(ts, str):
#                     if 'T' in ts:  # ISO format: 2025-12-17T10:30:00.123456
#                         reg_date = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00')).date()
#                     elif '.' in ts:  # With milliseconds
#                         reg_date = datetime.datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S").date()
#                     else:
#                         reg_date = datetime.datetime.strptime(ts[:19], "%Y-%m-%d %H:%M:%S").date()
#                 else:
#                     continue
#                 if reg_date == today:
#                     today_registrations += 1
#             except Exception as e:
#                 print(f"Timestamp parse error: {ts} → {e}")
#                 continue
            
#         recent_activities = []
        
#         def add_activity(act_type, title, desc, time_str):
#             recent_activities.append({
#                 'type': act_type,
#                 'title': title,
#                 'description': desc,
#                 'time': time_str
#             })
            
#         timestamped_records = []
#         for item in all_data:
#             ts_raw = item.get('timestamp')
#             if not ts_raw:
#                 continue
#             try:
#                 if isinstance(ts_raw, str):
#                     if 'T' in ts_raw:
#                         parsed_ts = datetime.datetime.fromisoformat(ts_raw.replace('Z', '+00:00'))
#                     elif '.' in ts_raw:
#                         parsed_ts = datetime.datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S.%f")
#                     else:
#                         parsed_ts = datetime.datetime.strptime(ts_raw, "%Y-%m-%d %H:%M:%S")
#                 else:
#                     continue
#                 timestamped_records.append((parsed_ts, item))
#             except Exception as e:
#                 print(f"Failed to parse timestamp {ts_raw}: {e}")
#                 continue
            
#         timestamped_records.sort(key=lambda x: x[0], reverse=True)
        
#         for parsed_ts, item in timestamped_records[:10]:
#             item_type = item.get('type')
#             name = item.get('name', 'Someone')
#             time_str = parsed_ts.strftime("%b %d, %Y at %I:%M %p")
            
#             if item_type == 'Registration':
#                 add_activity('user_registered', "New User Registered", f"{name} joined the platform", time_str)
                
#             elif item_type in ['CertificateRequest', 'certificate_requested', 'CertRequest']:
#                 status = item.get('status', 'pending').lower()
#                 if status == 'pending':
#                     add_activity('certificate_requested', "Certificate Request Received", f"{name} submitted a certificate request", time_str)
#                 elif status == 'verified':
#                     add_activity('certificate_verified', "Certificate Approved", f"{name}'s certificate was verified and approved", time_str)
#                 elif status == 'rejected':
#                     add_activity('certificate_rejected', "Certificate Rejected", f"{name}'s certificate request was rejected", time_str)
                    
#         context.update({
#             'total_users': len(users),
#             'pending_requests': len(pending_requests),
#             'verified_certificates': len(verified_certificates),
#             'rejected_requests': len(rejected_requests),
#             'today_registrations': today_registrations,
#             'total_certificates': total_certificates,
#             'recent_activities': recent_activities,
#         })
        
#         print("Dashboard data loaded successfully.")
        
#     except Exception as e:
#         print("CRITICAL ERROR in admin_dashboard:", str(e))
#         import traceback
#         traceback.print_exc()
#         messages.error(request, "Failed to load dashboard data. Check server connection or logs.")
        
#     return render(request, 'admin/admin_dashboard.html')

from django.shortcuts import render, redirect
from django.utils.timezone import now


def admin_dashboard(request):

    admin = request.session.get('data')
    if not admin or admin.get('role') != 'admin':
        return redirect('admin_login')

    blockchain_users = retrieveData()
    if isinstance(blockchain_users, str):
        blockchain_users = []

    total_users = len(blockchain_users)

    pending_requests = CertificateRequest.objects.filter(status='pending').count()
    verified_certificates = CertificateRequest.objects.filter(status='accepted').count()
    rejected_requests = CertificateRequest.objects.filter(status='rejected').count()

    today_registrations = CertificateRequest.objects.filter(
        request_date__date=now().date()
    ).count()

    total_certificates = CertificateRequest.objects.count()

    recent_activities = CertificateRequest.objects.order_by('-request_date')[:5]

    context = {
        'total_users': total_users,
        'pending_requests': pending_requests,
        'verified_certificates': verified_certificates,
        'rejected_requests': rejected_requests,
        'today_registrations': today_registrations,
        'total_certificates': total_certificates,
        'recent_activities': recent_activities,
    }

    return render(request, 'admin/admin_dashboard.html', context)

def user_management(request):
    print(request.session.get('data')['role'] )
    if request.session.get('data')['role'] != 'admin':
        messages.error(request, "Access denied. Admin login required.")
        return redirect('index')

    try:
        all_data = retrieveData()
        if not isinstance(all_data, list):
            raise Exception("Invalid data from blockchain")
        
        registration_records = [item for item in all_data if item.get('type') == 'Registration']
        
        users = []
        for item in registration_records:
            status_val = item.get('status', False)
            if status_val == True:
                status_str = 'approved'
            elif status_val == False:
                status_str = 'pending' 
                status_str = 'pending'
                
            users.append({
                'name': item.get('name', 'Unknown'),
                'email': item.get('email', ''),
                'reg_id': item.get('reg_id', 'N/A'),
                'timestamp': item.get('timestamp', ''),
                'status': status_str,
                'sumID': item.get('sumID'), 
            })
            
        total_users = len(users)
        pending_users = len([u for u in users if u['status'] == 'pending'])
        approved_users = len([u for u in users if u['status'] == 'approved'])
        rejected_users = len([u for u in users if u['status'] == 'rejected'])
        
        context = {
            'total_users': total_users,
            'pending_users': pending_users,
            'approved_users': approved_users,
            'rejected_users': rejected_users,
            'users': users,
        }
        
    except Exception as e:
        print("User Management Error:", e)
        messages.error(request, "Error loading user data.")
        context = {
            'total_users': 0,
            'pending_users': 0,
            'approved_users': 0,
            'rejected_users': 0,
            'users': []
        }
    return render(request, 'admin/user_management.html', context)


def update_user_status(request):
    if request.method != "POST":
        messages.error(request, "Invalid request.")
        return redirect('user_management')

    if request.session.get('data')['role'] != 'admin':
        messages.error(request, "Access denied. Admin login required.")
        return redirect('index')

    reg_id = request.POST.get('user_id')
    action = request.POST.get('action') 
    reason = request.POST.get('reason', '')

    if not reg_id or not action:
        messages.error(request, "Missing data.")
        return redirect('user_management')

    try:
        all_data = retrieveData()
        if not isinstance(all_data, list):
            raise Exception("Failed to retrieve blockchain data")

        updated = False
        for item in all_data:
            if item.get('type') == 'Registration' and item.get('reg_id') == reg_id:
                position = item.get('sumID') 
                
                if action == 'approve':
                    item['status'] = True
                    messages.success(request, f"User '{item['name']}' ({reg_id}) has been APPROVED.")
                elif action == 'reject':
                    item['status'] = False
                    item['rejected'] = True
                    item['reject_reason'] = reason or "No reason provided"
                    messages.success(request, f"User '{item['name']}' ({reg_id}) has been REJECTED.")
                else:
                    messages.error(request, "Invalid action.")
                    return redirect('user_management')
                
                result = updateData(position, item)
                if result == "Success":
                    updated = True
                else:
                    raise Exception(f"Blockchain update failed: {result}")
                break
            
        if not updated:
            messages.error(request, "User not found.")
        else:
            messages.success(request, "User status updated successfully on blockchain!")
            
    except Exception as e:
        print("Update Status Error:", e)
        messages.error(request, f"Failed to update status: {str(e)}")
        
    return redirect('user_management')



# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import CertificateRequest
import os
from django.conf import settings

def admin_requests(request):
    """Admin view to see all certificate requests"""
    if request.session.get('email') != 'admin@gmail.com':
        messages.error(request, 'Admin access required')
        return redirect('login')
    
    # Get all requests
    all_requests = CertificateRequest.objects.all()
    
    # Get stats
    total_requests = all_requests.count()
    pending_requests = all_requests.filter(status='pending').count()
    accepted_requests = all_requests.filter(status='accepted').count()
    rejected_requests = all_requests.filter(status='rejected').count()
    
    # Pagination
    paginator = Paginator(all_requests, 10)  # Show 10 requests per page
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)
    
    context = {
        'requests': requests_page,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'rejected_requests': rejected_requests,
    }
    
    return render(request, 'admin/admin_requests.html', context)

# def accept_certificate_request(request):
#     """Admin accepts a certificate request and uploads certificate"""
#     if request.session.get('email') != 'admin@gmail.com':
#         messages.error(request, 'Admin access required')
#         return redirect('login')
    
#     if request.method == 'POST':
#         try:
#             request_id = request.POST.get('request_id')
#             reg_id = request.POST.get('reg_id')
#             certificate_name = request.POST.get('certificate_name')
#             remarks = request.POST.get('remarks', '')
#             blockchain_hash = request.POST.get('blockchain_hash', '')
#             certificate_file = request.FILES.get('certificate_file')
            
#             if not certificate_file:
#                 messages.error(request, 'Please upload the certificate file')
#                 return redirect('admin_requests')
            
#             # Get the certificate request
#             cert_request = get_object_or_404(CertificateRequest, id=request_id, reg_id=reg_id)
            
#             # Update the request status
#             cert_request.status = 'accepted'
#             cert_request.accepted_date = timezone.now()
#             cert_request.admin_remarks = remarks
#             cert_request.blockchain_hash = blockchain_hash
#             cert_request.save()
            
#             url = "http://127.0.0.1:5000/upload/"
#             payload = {}
#             files = [('file', certificate_file)]
#             headers = {}
            
#             response = requests.post(url, headers=headers, data=payload, files=files)
#             gg = response.json()
#             print("IPFS Response:", gg)
            
#             if "Success" in gg:
#                 blockchain = addNewData({
#                     "Type": "File_Upload",
#                     'request_id' : request_id,
#                     'reg_id' : reg_id,
#                     'certificate_name' : certificate_name,
#                     'remarks' : remarks,
#                     'blockchain_hash' : blockchain_hash,
#                     'certificate_file' : certificate_file,
#                 })
#                 print("File Upload to Blockchain status:", blockchain)
            
#             # Handle file upload
#             if certificate_file:
#                 # Create directory if not exists
#                 upload_dir = os.path.join(settings.MEDIA_ROOT, 'certificates', reg_id)
#                 os.makedirs(upload_dir, exist_ok=True)
                
#                 # Generate unique filename
#                 file_extension = os.path.splitext(certificate_file.name)[1]
#                 filename = f"cert_{request_id}_{int(timezone.now().timestamp())}{file_extension}"
#                 file_path = os.path.join(upload_dir, filename)
                
#                 # Save the file
#                 with open(file_path, 'wb+') as destination:
#                     for chunk in certificate_file.chunks():
#                         destination.write(chunk)
                
#                 # Save file path to database (you might want to add a field for this)
#                 cert_request.certificate_file = f'certificates/{reg_id}/{filename}'
#                 cert_request.save()
            
#             # You can add additional logic here:
#             # 1. Send email notification to student
#             # 2. Store certificate in blockchain (if using)
#             # 3. Log the action
            
#             messages.success(
#                 request, 
#                 f'Certificate request accepted and uploaded successfully for {cert_request.user_name}!'
#             )
            
#         except CertificateRequest.DoesNotExist:
#             messages.error(request, 'Certificate request not found')
#         except Exception as e:
#             messages.error(request, f'Error accepting request: {str(e)}')
    
#     return redirect('admin_requests')


def accept_certificate_request(request):
    """Admin accepts a certificate request and uploads to IPFS + blockchain"""
    if request.session.get('email') != 'admin@gmail.com':
        messages.error(request, 'Admin access required')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            request_id = request.POST.get('request_id')
            reg_id = request.POST.get('reg_id')
            certificate_name = request.POST.get('certificate_name')
            remarks = request.POST.get('remarks', '')
            blockchain_hash = request.POST.get('blockchain_hash', '')
            certificate_file = request.FILES.get('certificate_file')
            
            if not certificate_file:
                messages.error(request, 'Please upload the certificate file')
                return redirect('admin_requests')
            
            # Get the certificate request
            cert_request = get_object_or_404(CertificateRequest, id=request_id, reg_id=reg_id)
            
            # 1. Upload to IPFS
            url = "http://127.0.0.1:5000/upload/"
            files = [('file', certificate_file)]
            
            response = requests.post(url, files=files)
            ipfs_response = response.json()
            print("IPFS Response:", ipfs_response)
            
            if "Success" not in ipfs_response:
                messages.error(request, f'Failed to upload to IPFS: {ipfs_response}')
                return redirect('admin_requests')
            
            ipfs_cid = ipfs_response.get("Success")
            
            # 2. Store in Blockchain (your existing code)
            blockchain_data = {
                "Type": "Certificate_Upload",
                'request_id': request_id,
                'reg_id': reg_id,
                'certificate_name': certificate_name,
                'remarks': remarks,
                'ipfs_cid': ipfs_cid,
                'file_type': certificate_file.name.split('.')[-1] if '.' in certificate_file.name else 'pdf',
                'uploaded_by': request.session.get('email', 'admin@gmail.com'),
                'upload_date': timezone.now().isoformat(),
                'student_name': cert_request.user_name,
                'original_filename': certificate_file.name,
                'file_size': certificate_file.size
            }
            
            # Use your existing addNewData function
            blockchain_result = addNewData(blockchain_data)
            print("Blockchain upload status:", blockchain_result)
            
            # 3. Update database record
            cert_request.status = 'accepted'
            cert_request.accepted_date = timezone.now()
            cert_request.admin_remarks = remarks
            cert_request.blockchain_hash = ipfs_cid  # Store IPFS CID
            cert_request.verified_by = request.session.get('email', 'admin@gmail.com')
            cert_request.verified_date = timezone.now()
            cert_request.save()
            
            messages.success(
                request, 
                f'Certificate accepted and stored on IPFS/Blockchain for {cert_request.user_name}! '
                f'IPFS CID: {ipfs_cid}'
            )
            
        except CertificateRequest.DoesNotExist:
            messages.error(request, 'Certificate request not found')
        except requests.RequestException as e:
            messages.error(request, f'Error connecting to IPFS server: {str(e)}')
        except Exception as e:
            messages.error(request, f'Error accepting request: {str(e)}')
    
    return redirect('admin_requests')




def reject_certificate_request(request):
    """Admin rejects a certificate request"""
    if request.session.get('email') != 'admin@gmail.com':
        messages.error(request, 'Admin access required')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            request_id = request.POST.get('request_id')
            reg_id = request.POST.get('reg_id')
            reject_reason = request.POST.get('reject_reason')
            reject_details = request.POST.get('reject_details', '')
            
            # Get the certificate request
            cert_request = get_object_or_404(CertificateRequest, id=request_id, reg_id=reg_id)
            
            # Update the request status
            cert_request.status = 'rejected'
            cert_request.rejected_date = timezone.now()
            cert_request.reject_reason = reject_reason
            cert_request.reject_details = reject_details
            cert_request.save()
            
            # You can add additional logic here:
            # 1. Send email notification to student
            # 2. Log the action
            
            messages.warning(
                request, 
                f'Certificate request rejected for {cert_request.user_name}. Reason: {reject_reason}'
            )
            
        except CertificateRequest.DoesNotExist:
            messages.error(request, 'Certificate request not found')
        except Exception as e:
            messages.error(request, f'Error rejecting request: {str(e)}')
    
    return redirect('admin_requests')




from django.core.paginator import Paginator
def user_dashboard(request):
    """User dashboard with dynamic data from database and blockchain"""
    if 'reg_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    reg_id = request.session.get('reg_id')
    user_name = request.session.get('u', {}).get('name', 'User')
    
    # 1. Get ALL user's certificate requests from the database
    user_requests = CertificateRequest.objects.filter(reg_id=reg_id)
    
    # 2. Calculate Statistics (Dynamic)
    total_certificates = user_requests.count()
    claimed_certificates = user_requests.filter(status='accepted').count()
    pending_certificates = user_requests.filter(status='pending').count()
    rejected_certificates = user_requests.filter(status='rejected').count()
    
    # 3. Prepare Recent Activities from database records
    recent_activities = []
    for req in user_requests.order_by('-request_date')[:10]:  # Last 10 requests
        if req.status == 'accepted':
            title = f"Certificate Accepted: {req.certificate_name}"
            status_label = 'claimed'
            timestamp = req.accepted_date or req.request_date
        elif req.status == 'rejected':
            title = f"Certificate Rejected: {req.certificate_name}"
            status_label = 'rejected'
            timestamp = req.rejected_date or req.request_date
        else:  # pending
            title = f"Certificate Requested: {req.certificate_name}"
            status_label = 'pending'
            timestamp = req.request_date
        
        recent_activities.append({
            'title': title,
            'description': f"Request ID: #{req.id}",
            'timestamp': timestamp,
            'status': status_label,
            'certificate_id': req.id,
        })
    
    # 4. Get My Certificates (Accepted ones with blockchain/IPFS info)
    my_certificates = []
    accepted_requests = user_requests.filter(status='accepted')
    
    # Try to fetch blockchain data for context (optional)
    blockchain_data_map = {}
    try:
        all_blockchain_data = retrieveData()  # Your Web3 function
        if isinstance(all_blockchain_data, list):
            for data in all_blockchain_data:
                if isinstance(data, dict) and 'request_id' in data:
                    blockchain_data_map[data['request_id']] = data
    except Exception as e:
        print(f"Could not fetch blockchain data for dashboard: {e}")
        # Continue without blockchain data
    
    for cert in accepted_requests:
        cert_data = {
            'id': cert.id,
            'title': cert.certificate_name,
            'certificate_id': f"#{cert.id}",
            'status': 'claimed',
            'request_date': cert.request_date,
            'blockchain_hash': cert.blockchain_hash,
        }
        
        # Add IPFS download URL if hash exists
        if cert.blockchain_hash:
            # Determine file type (default to pdf)
            file_type = 'pdf'
            block_data = blockchain_data_map.get(str(cert.id))
            if block_data and block_data.get('file_type'):
                file_type = block_data['file_type']
            
            cert_data['download_url'] = f"http://127.0.0.1:5000/download/{cert.blockchain_hash}/{file_type}"
            cert_data['ipfs_cid'] = cert.blockchain_hash
            cert_data['file_type'] = file_type
        
        my_certificates.append(cert_data)
    
    # 5. Get pending requests for the "Quick Actions" section
    pending_requests = user_requests.filter(status='pending').count()
    
    context = {
        # User Info
        'user_name': user_name,
        'reg_id': reg_id,
        
        # Stats
        'total_certificates': total_certificates,
        'claimed_certificates': claimed_certificates,
        'pending_certificates': pending_certificates,
        'rejected_certificates': rejected_certificates,
        
        # Dynamic Data
        'recent_activities': recent_activities,
        'my_certificates': my_certificates[:5],  # Show only 5 in dashboard
        
        # For the modal form
        'new_request_url': '/user/new-certificate-request/',  # Your actual URL name
    }
    
    return render(request, 'user/user_dashboard.html', context)


def new_certificate_request(request):
    """Display the certificate request form"""
    if 'reg_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    return render(request, 'user/new_certificate_request.html')



def submit_certificate_request(request):
    """Handle certificate request submission"""
    if 'reg_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Get form data
            certificate_name = request.POST.get('certificate_name')
            
            # Handle "Other" certificate type
            if certificate_name == 'Other':
                certificate_name = request.POST.get('other_certificate_name')
                if not certificate_name:
                    messages.error(request, 'Please specify certificate name')
                    return redirect('new_certificate_request')
            
            certificate_description = request.POST.get('certificate_description', '')
            
            # Get user info from session
            reg_id = request.session.get('reg_id')
            user_name = request.session.get('u', {}).get('name', 'User')
            
            if not reg_id:
                messages.error(request, 'User information not found. Please login again.')
                return redirect('login')
            
            # Check if user already has a pending request for this certificate
            existing_request = CertificateRequest.objects.filter(
                reg_id=reg_id,
                certificate_name=certificate_name,
                status='pending'
            ).exists()
            
            if existing_request:
                messages.warning(request, f'You already have a pending request for "{certificate_name}"')
                return redirect('user_dashboard')
            
            # Create new certificate request
            certificate_request = CertificateRequest.objects.create(
                reg_id=reg_id,
                user_name=user_name,
                certificate_name=certificate_name,
                status='pending',
                request_date=timezone.now()
            )
            
            # You can add additional logic here, like:
            # 1. Send email notification to admin
            # 2. Log the request
            # 3. Store additional description in another model if needed
            
            messages.success(
                request, 
                f'Certificate request for "{certificate_name}" submitted successfully! '
                'Admin will review your request soon.'
            )
            return redirect('user_dashboard')
            
        except Exception as e:
            messages.error(request, f'Error submitting request: {str(e)}')
            return redirect('new_certificate_request')
    
    # If not POST request, redirect to request form
    return redirect('new_certificate_request')





# def my_certificates(request):
#     """View for users to see their certificates"""
#     if 'reg_id' not in request.session:
#         messages.error(request, 'Please login first')
#         return redirect('login')
    
#     reg_id = request.session.get('reg_id')
#     user_name = request.session.get('u', {}).get('name', 'User')
    
#     # Get user's certificates
#     certificates = CertificateRequest.objects.filter(reg_id=reg_id)
    
#     # Get stats
#     total_certificates = certificates.count()
#     verified_certificates = certificates.filter(status='accepted').count()
#     pending_certificates = certificates.filter(status='pending').count()
#     rejected_certificates = certificates.filter(status='rejected').count()
    
#     # Add file URL to each certificate
#     for cert in certificates:
#         if cert.certificate_file:
#             # You might need to adjust this based on your file storage
#             cert.file_url = cert.certificate_file.url
    
#     context = {
#         'certificates': certificates,
#         'total_certificates': total_certificates,
#         'verified_certificates': verified_certificates,
#         'pending_certificates': pending_certificates,
#         'rejected_certificates': rejected_certificates,
#         'user_name': user_name,
#     }
    
#     return render(request, 'user/my_certificates.html', context)


def my_certificates(request):
    """View for users to see their certificates"""
    if 'reg_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    reg_id = request.session.get('reg_id')
    user_name = request.session.get('u', {}).get('name', 'User')
    
    # Get user's certificates with pagination
    certificates_list = CertificateRequest.objects.filter(reg_id=reg_id).order_by('-request_date')
    
    # Get stats
    total_certificates = certificates_list.count()
    verified_certificates = certificates_list.filter(status='accepted').count()
    pending_certificates = certificates_list.filter(status='pending').count()
    rejected_certificates = certificates_list.filter(status='rejected').count()
    
    # Add IPFS URL to each accepted certificate
    for cert in certificates_list:
        if cert.status == 'accepted' and cert.blockchain_hash:
            # Create direct IPFS download URL
            cert.ipfs_url = f"http://127.0.0.1:5000/download/{cert.blockchain_hash}/pdf"
            cert.file_type = 'pdf'  # Default to PDF
    
    # Pagination
    paginator = Paginator(certificates_list, 9)  # Show 9 certificates per page
    page_number = request.GET.get('page')
    certificates = paginator.get_page(page_number)
    
    context = {
        'certificates': certificates,
        'total_certificates': total_certificates,
        'verified_certificates': verified_certificates,
        'pending_certificates': pending_certificates,
        'rejected_certificates': rejected_certificates,
        'user_name': user_name,
    }
    
    return render(request, 'user/my_certificates.html', context)



# def download_certificate(request, certificate_id):
#     """Download certificate file"""
#     if 'reg_id' not in request.session:
#         messages.error(request, 'Please login first')
#         return redirect('login')
    
#     try:
#         cert = CertificateRequest.objects.get(
#             id=certificate_id,
#             reg_id=request.session.get('reg_id'),
#             status='accepted'
#         )
        
#         if cert.certificate_file:
#             # Return the file for download
#             response = HttpResponse(cert.certificate_file, content_type='application/octet-stream')
#             response['Content-Disposition'] = f'attachment; filename="{cert.certificate_name}.pdf"'
#             return response
#         else:
#             messages.error(request, 'Certificate file not found')
#             return redirect('my_certificates')
            
#     except CertificateRequest.DoesNotExist:
#         messages.error(request, 'Certificate not found or not verified')
#         return redirect('my_certificates')
#     except Exception as e:
#         messages.error(request, f'Error downloading certificate: {str(e)}')
#         return redirect('my_certificates')

def download_certificate(request, certificate_id):
    """Download certificate file from IPFS"""
    if 'reg_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    try:
        # Get the certificate
        cert = CertificateRequest.objects.get(
            id=certificate_id,
            reg_id=request.session.get('reg_id'),
            status='accepted'
        )
        
        # Check if certificate has IPFS CID stored in blockchain
        if not cert.blockchain_hash:
            messages.error(request, 'Certificate not stored on IPFS')
            return redirect('my_certificates')
        
        # Your existing Web3 code to retrieve data
        # First, get all blockchain data
        try:
            all_data = retrieveData()
            certificate_data = None
            
            # Find this certificate in blockchain data
            for data in all_data:
                if isinstance(data, dict) and data.get('request_id') == str(certificate_id):
                    certificate_data = data
                    break
            
            if not certificate_data:
                messages.error(request, 'Certificate not found on blockchain')
                return redirect('my_certificates')
            
            # Get IPFS CID from blockchain data
            ipfs_cid = certificate_data.get('ipfs_cid') or cert.blockchain_hash
            
            if not ipfs_cid:
                messages.error(request, 'IPFS CID not found')
                return redirect('my_certificates')
            
            # Determine file type from certificate name or stored data
            file_type = 'pdf'  # Default to PDF
            if cert.certificate_file:
                # Try to get extension from original filename
                original_name = cert.certificate_file.name
                if '.' in original_name:
                    file_type = original_name.split('.')[-1].lower()
            elif certificate_data.get('file_type'):
                file_type = certificate_data.get('file_type')
            
            # Download from IPFS via your Helia server
            ipfs_url = f"http://127.0.0.1:5000/download/{ipfs_cid}/{file_type}"
            
            try:
                # Make request to your IPFS server
                response = requests.get(ipfs_url, stream=True)
                
                if response.status_code == 200:
                    # Get file size from headers
                    file_size = int(response.headers.get('Content-Length', 0))
                    
                    # Create HTTP response with file data
                    django_response = HttpResponse(
                        response.content,
                        content_type='application/octet-stream'
                    )
                    
                    # Set filename
                    safe_filename = f"{cert.certificate_name.replace(' ', '_')}.{file_type}"
                    django_response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
                    django_response['Content-Length'] = file_size
                    
                    # Log download
                    print(f"Downloading certificate {certificate_id} from IPFS: {ipfs_cid}")
                    
                    return django_response
                else:
                    messages.error(request, f'Failed to download from IPFS. Status: {response.status_code}')
                    return redirect('my_certificates')
                    
            except requests.RequestException as e:
                messages.error(request, f'Error connecting to IPFS server: {str(e)}')
                return redirect('my_certificates')
            
        except Exception as e:
            messages.error(request, f'Error retrieving blockchain data: {str(e)}')
            return redirect('my_certificates')
            
    except CertificateRequest.DoesNotExist:
        messages.error(request, 'Certificate not found or not verified')
        return redirect('my_certificates')
    except Exception as e:
        messages.error(request, f'Error downloading certificate: {str(e)}')
        return redirect('my_certificates')


def delete_certificate(request, certificate_id):
    """Delete a certificate (soft delete)"""
    if 'reg_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    try:
        cert = CertificateRequest.objects.get(
            id=certificate_id,
            reg_id=request.session.get('reg_id')
        )
        
        # Soft delete by updating status
        cert.status = 'deleted'
        cert.save()
        
        messages.success(request, f'Certificate "{cert.certificate_name}" deleted successfully')
        
    except CertificateRequest.DoesNotExist:
        messages.error(request, 'Certificate not found')
    except Exception as e:
        messages.error(request, f'Error deleting certificate: {str(e)}')
    
    return redirect('my_certificates')




# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from .models import CertificateRequest

def request_status(request):
    """View for users to see their request status"""
    if 'reg_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    reg_id = request.session.get('reg_id')
    user_name = request.session.get('u', {}).get('name', 'User')
    
    # Get user's requests
    user_requests = CertificateRequest.objects.filter(reg_id=reg_id).order_by('-request_date')
    
    # Get stats
    total_requests = user_requests.count()
    pending_requests = user_requests.filter(status='pending').count()
    accepted_requests = user_requests.filter(status='accepted').count()
    rejected_requests = user_requests.filter(status='rejected').count()
    
    # Pagination
    paginator = Paginator(user_requests, 10)  # Show 10 requests per page
    page_number = request.GET.get('page')
    requests_page = paginator.get_page(page_number)
    
    context = {
        'requests': requests_page,
        'total_requests': total_requests,
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'rejected_requests': rejected_requests,
        'user_name': user_name,
    }
    
    return render(request, 'user/request_status.html', context)

def request_detail(request, request_id):
    """View detailed information about a specific request"""
    if 'reg_id' not in request.session:
        messages.error(request, 'Please login first')
        return redirect('login')
    
    try:
        cert_request = CertificateRequest.objects.get(
            id=request_id,
            reg_id=request.session.get('reg_id')
        )
        
        context = {
            'request': cert_request,
        }
        
        return render(request, 'request_detail.html', context)
        
    except CertificateRequest.DoesNotExist:
        messages.error(request, 'Request not found')
        return redirect('request_status')