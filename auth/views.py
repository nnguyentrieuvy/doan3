from django.shortcuts import render, redirect
import connection
import hashlib

# Create your views here.


def TK(tk):
    DVX = connection.connect_db()
    TK = DVX["TaiKhoan"]
    data = TK.find({"TaiKhoan": tk})
    for d in data:
        a = d
    return a

def index(request):
    m = ''
    print(-2)
    if 'tk' in request.session and 'mk' in request.session and 'vtro' in request.session:
        try:
            d = TK(request.session['tk'])
            if request.session['tk'] == d['TaiKhoan'] and request.session['mk'] == d['MatKhau']:
                if request.session['vtro'] == 0 or request.session['vtro'] == 1 or request.session['vtro'] == 2:
                    return redirect('../usr/0')
        except UnboundLocalError:
            return redirect('../admin')
    else:
            m = 'Tài khoản hoặc mật khẩu không đúng!'
    return render(request, 'Admin/login.html', {'message': m})

def login(request):
    print(-1)
    if 'tk' in request.session and 'mk' in request.session and 'vtro' in request.session:
        print(0)
        try:
            d = TK(request.session['tk'])
            if request.session['tk'] == d['TaiKhoan'] and request.session['mk'] == d['MatKhau']:
                if request.session['vtro'] == 0:
                    return render(request, 'Admin/admin.html')
                elif request.session['vtro'] == 1:
                    return render(request, 'NVTD/index.html')
                elif request.session['vtro'] == 2:
                    return render(request, 'NVSV/index.html')
        except UnboundLocalError:
            return redirect('../admin')
    if request.method == 'POST':
        tk = request.POST['tk']
        mk = request.POST['mk']
        hash_object = hashlib.sha1(bytes(mk, 'utf-8'))
        mk = hash_object.hexdigest()
        try:
            d = TK(tk)
            if d['TaiKhoan'] == tk and d['MatKhau'] == mk:
                request.session['tk'] = tk
                request.session['mk'] = mk
                request.session['vtro'] = d['VaiTro']

                print("vtro la")
                print(request.session['vtro'])
                if d['VaiTro'] == 0:
                    print(2)
                    return render(request, 'Admin/admin.html')
                elif d['VaiTro'] == 1:
                    return render(request, 'NVTD/index.html')
                elif d['VaiTro'] == 2:
                    return render(request, 'NVSV/index.html')
        except UnboundLocalError:
            return redirect('../admin')
    print(4)
    return redirect('../admin')

def logout(request):
    if 'tk' in request.session and 'mk' in request.session:
        del request.session['tk']
        del request.session['mk']
        del request.session['vtro']
        return render(request, 'Admin/login.html')
    else:
        return redirect('../admin')

