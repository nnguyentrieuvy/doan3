import connection

def TK(tk):
    DVX = connection.connect_db()
    TK = DVX["TaiKhoan"]
    data = TK.find({"TaiKhoan": tk})
    for d in data:
        a = d
    return a

# def check(request):
#     vtro = -1
#     if 'tk' in request.session and 'mk' in request.session and 'vtro' in request.session:
#         vtro = request.session['vtro']
#         tk = request.session['tk']
#         print('hhhh')
#         try:
#             d = TK(tk)
#             if request.session['tk'] == d['TaiKhoan'] and request.session['mk'] == d['MatKhau'] and request.session['vtro'] == d['VaiTro']:
#                 return vtro
#         except UnboundLocalError:
#             return vtro
#     return vtro

def check(request):
    vtro = -1
    if 'tk' in request.session and 'mk' in request.session and 'vtro' in request.session:
        vtro = request.session['vtro']
        tk = request.session['tk']
        print('hhhh')
        d = TK(tk)
        if request.session['tk'] == d['TaiKhoan'] and request.session['mk'] == d['MatKhau'] and request.session[
            'vtro'] == d['VaiTro']:
            return vtro
    return vtro

def del_session(request):
    if 'tk' in request.session and 'mk' in request.session and 'vtro' in request.session:
        del request.session['tk']
        del request.session['mk']
        del request.session['vtro']