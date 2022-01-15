import json

from bson import ObjectId
from django.shortcuts import render, redirect
# from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
import check_permission
import connection
from pymongo.errors import BulkWriteError
from django.utils.datastructures import MultiValueDictKeyError
import hashlib
import connection
from django.views.decorators.csrf import csrf_exempt
from djongo.database import IntegrityError, DatabaseError
from djongo import models
from home.models import Tuyen, LoTrinh
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime, timedelta

# Create your views here.

def TK(tk):
    DVX = connection.connect_db()
    TK = DVX["TaiKhoan"]
    data = TK.find({"TaiKhoan": tk})
    for d in data:
        a = d
    return a

def dangky(request):
    DVX = connection.connect_db()
    tk = DVX["TaiKhoan"]
    try:
        if request.method == 'POST':
            taikhoan = request.POST['TK']
            matkhau = request.POST['MK']
            matkhau = hashlib.sha1(bytes(matkhau, 'utf-8'))
            matkhau = matkhau.hexdigest()

            xnmk = request.POST['xnmk']
            xnmk = hashlib.sha1(bytes(xnmk, 'utf-8'))
            xnmk = xnmk.hexdigest()
            if matkhau == xnmk:
                doc = {"TaiKhoan": taikhoan, "MatKhau": matkhau, "VaiTro": 3}
                tk.insert_one(doc)
                return render(request, 'KH/index.html')
    except MultiValueDictKeyError:
        return render(request, 'KH/index.html')
    return render(request, 'KH/index.html')

def index(request):
    m = ''
    print(-2)
    if 'tk' in request.session and 'mk' in request.session and 'vtro' in request.session:
        try:
            d = TK(request.session['tk'])
            if request.session['tk'] == d['TaiKhoan'] and request.session['mk'] == d['MatKhau']:
                if request.session['vtro'] == 3:
                    return redirect('../customer/0')
        except UnboundLocalError:
            return redirect('../Home/index.html')
    else:
        m = 'Tài khoản hoặc mật khẩu không đúng!'
    return render(request, 'Home/index.html')




def login(request):
    try:
        if request.method == 'POST':
            tk = request.POST['tk']
            mk = request.POST['mk']
            hash_object = hashlib.sha1(bytes(mk, 'utf-8'))
            mk = hash_object.hexdigest()
            print(mk)
            d = TK(tk)
            if d['TaiKhoan'] == tk and d['MatKhau'] == mk:
                request.session['tk'] = tk
                request.session['mk'] = mk
                request.session['vtro'] = d['VaiTro']
                if d['VaiTro'] == 3:
                    return redirect('../customer/0')
    except MultiValueDictKeyError:
        return render(request, 'Home/login.html')
    return render(request, 'Home/login.html')

def registration(request):
    return render(request, 'Home/registration.html')

def lichtrinh(request):
    DVX = connection.connect_db()
    lt = DVX['LoTrinh']
    lt_ttr = lt.aggregate([
        {'$lookup':
             {'from': 'Tuyen_Tram',
              # 'let': {'n': {"$size": "$MaTuyen"}},
              'localField': 'MaTuyen',
              'foreignField': 'MaTuyen',
              # 'pipeline': [query10],
              'as': 'MaTuyen'}},
        {"$group": {
            "_id": "$_id",
            "TGXB": {"$first": "$TGXuatBen"},
            "TGDB": {"$first": "$TGDenBen"},
            "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
            "Tram": {"$first": "$MaTuyen.MaTram"},
            "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
            "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
        }
        },
        {'$lookup':
             {'from': 'Tuyen',
              # 'let': {'n': {"$size": "$MaTuyen"}},
              'localField': 'MaTuyen',
              'foreignField': '_id',
              # 'pipeline': [query10],
              'as': 'MaTuyen'}},
        ])
    lt_ttr = list(lt_ttr)
    print(lt_ttr)
    return render(request, 'Home/lichtrinh.html', {'data': lt_ttr})

def search(request):
    if request.method == 'GET':
        bxp = request.GET['bxp']
        bd = request.GET['bd']
        if bxp == "":
            bxp = ["$ne", ""]
        else:
            bxp = [bxp]
            bxp = ["$in", bxp]

        if bd == "":
            bd= ["$ne", ""]
        else:
            bd = [bd]
            bd = ["$in", bd]
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        lt_ttr = lt.aggregate([
            {'$lookup':
                 {'from': 'Tuyen_Tram',
                  # 'let': {'n': {"$size": "$MaTuyen"}},
                  'localField': 'MaTuyen',
                  'foreignField': 'MaTuyen',
                  # 'pipeline': [query10],
                  'as': 'MaTuyen'}},
            {"$group": {
                "_id": "$_id",
                "TGXB": {"$first": "$TGXuatBen"},
                "TGDB": {"$first": "$TGDenBen"},
                "SoVe": {"$first": "$SoVe"},
                "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
                "Tram": {"$first": "$MaTuyen.MaTram"},
                "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
                "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
            }
            },
            {
                "$match": {
                    "TramDau.TenDuong": {bxp[0]: bxp[1]},
                    "TramCuoi.TenDuong": {bd[0]: bd[1]}
                }
            },
            {'$lookup':
                 {'from': 'Tuyen',
                  'localField': 'MaTuyen',
                  'foreignField': '_id',
                  'as': 'MaTuyen'}},
        ])
        lt_ttr = list(lt_ttr)
        print(lt_ttr)
    if check_permission.check(request) == 3:
        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sl_ve = sum(a['SL'] for a in i['cart'])
                break
            else:
                sl_ve = 0
        print('soveeee'+str(sl_ve))
        return render(request, 'KH/lichtrinh.html', {'data': lt_ttr, 'sove': sl_ve, 'tk': request.session['tk']})
    else:
        return render(request, 'Home/lichtrinh.html', {'data': lt_ttr})

def ltr(request, dd, xp, mt):
    DVX = connection.connect_db()
    lt = DVX['LoTrinh']
    lt_ttr = lt.aggregate([
        {'$lookup':
             {'from': 'Tuyen_Tram',
              # 'let': {'n': {"$size": "$MaTuyen"}},
              'localField': 'MaTuyen',
              'foreignField': 'MaTuyen',
              # 'pipeline': [query10],
              'as': 'MaTuyen'}},
        {"$group": {
                "_id": "$_id",
                 "TGXB": {"$first": "$TGXuatBen"},
                 "TGDB": {"$first": "$TGDenBen"},
                 "SoVe": {"$first": "$SoVe"},
                "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
                "Tram": {"$first": "$MaTuyen.MaTram"},
                "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
                "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
            }
        },
        {
            "$match": {
                "MaTuyen": mt
            }
        },
        {'$lookup':
             {'from': 'Tuyen',
              # 'let': {'n': {"$size": "$MaTuyen"}},
              'localField': 'MaTuyen',
              'foreignField': '_id',
              # 'pipeline': [query10],
              'as': 'MaTuyen'}},
    ])
    lt_ttr = list(lt_ttr)
    print(lt_ttr)
    print(lt_ttr[0]['Tram'])
    if check_permission.check(request) == 3:
        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sl_ve = sum(a['SL'] for a in i['cart'])
                break
            else:
                sl_ve = 0
        print('soveeee'+str(sl_ve))
        return render(request, 'KH/ltr.html', {'data': lt_ttr, 'tram': lt_ttr[0]['Tram'], 'sove': sl_ve, 'tk': request.session['tk']})
    else:
        return render(request, 'Home/ltr.html', {'data': lt_ttr, 'tram': lt_ttr[0]['Tram']})

def benxe(request):
    DVX = connection.connect_db()
    t_tr = DVX['Tuyen_Tram']
    t_tr = t_tr.aggregate([
        {
            "$group": {
                "_id": "$MaTuyen",
                "BenXuat": {"$first": "$MaTram"},
                "BenDen": {"$last": "$MaTram"}
            }
        },
        # {
        #     "$group": {
        #         "_id": "$_id",
        #         "TramDau": {"$first": "$BenXuat.TenDuong"},
        #         "TramCuoi": {"$first": "$BenDen.TenDuong"},
        #
        #
        #     }
        # },
        {
            "$group": {
                "_id": "$BenDen._id",
                "TramCuoi": {"$first": "$BenDen.TenDuong"}

            }
        }
    ])

    t_tr = list(t_tr)

    print(t_tr)
    if check_permission.check(request) == 3:
        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sl_ve = sum(a['SL'] for a in i['cart'])
                break
            else:
                sl_ve = 0
        return render(request, 'KH/benxe.html', {'data': t_tr, 'sove': sl_ve, 'tk':request.session['tk']})
    else:
        return render(request, 'Home/benxe.html', {'data': t_tr})


def bx_diemxp(request, dd, mtr):
    DVX = connection.connect_db()
    lt = DVX['LoTrinh']
    t_tr = DVX['Tuyen_Tram']
    t_tr = t_tr.aggregate([
        {
            "$group": {
                "_id": "$MaTuyen",
                "BenXuat": {"$first": "$MaTram"},
                "BenDen": {"$last": "$MaTram"}
            }
        },
        {
            "$match": {
                "BenDen._id": mtr
            }
        },
        {
            "$group": {
                "_id": "$BenXuat._id",
                "TramXuat": {"$first": "$BenXuat.TenDuong"},
                "TramDen": {"$first": "$BenDen.TenDuong"}

            }
        }
    ])

    t_tr = list(t_tr)

    print(t_tr)
    if check_permission.check(request) == 3:
        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sl_ve = sum(a['SL'] for a in i['cart'])
                break
            else:
                sl_ve = 0
        return render(request, 'KH/bx_diemxp.html', {'data': t_tr, 'dd': dd, 'sove': sl_ve, 'tk':request.session['tk']})
    else:
        return render(request, 'Home/bx_diemxp.html', {'data': t_tr, 'dd': dd})



def cttd(request, dd, xp):
    DVX = connection.connect_db()
    lt = DVX['LoTrinh']
    t_tr = DVX['Tuyen_Tram']
    t_tr = t_tr.aggregate([
        {
            "$group": {
                "_id": "$MaTuyen",
                "Tram": {"$push": "$MaTram"},
                "TramDau": {"$first": "$MaTram.TenDuong"},
                "TramCuoi": {"$last": "$MaTram.TenDuong"},
            }
        },
        {
            "$match": {
                "TramDau": xp,
                "TramCuoi": dd
            }
        },
    ])

    t_tr = list(t_tr)

    print(t_tr)
    if check_permission.check(request) == 3:
        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sl_ve = sum(a['SL'] for a in i['cart'])
                break
            else:
                sl_ve = 0
        return render(request, 'KH/chitiettd.html', {'data': t_tr, 'dd': dd, 'xp': xp, 'sove': sl_ve, 'tk':request.session['tk']})
    else:
        return render(request, 'Home/chitiettd.html', {'data': t_tr, 'dd': dd, 'xp': xp})

def login(request):
    print(-1)
    sl_ve = 0
    if 'tk' in request.session and 'mk' in request.session and 'vtro' in request.session:
        print(0)
        print(request.session['tk'])
        # try:
        d = TK(request.session['tk'])
        if request.session['tk'] == d['TaiKhoan'] and request.session['mk'] == d['MatKhau']:
            try:
                for i in request.session['cs_cart']:
                    if i['tk'] == request.session['tk']:
                        sl_ve = sum(a['SL'] for a in i['cart'])
                        break
                    else:
                        sl_ve = 0
            except KeyError:
                request.session['cs_cart'] = []
                sl_ve = 0
            return render(request, 'KH/index.html', {'sove': sl_ve, 'tk': request.session['tk']})
        else:
            del request.session['tk']
            del request.session['mk']
            del request.session['vtro']
            return render(request, 'Home/login.html')
        # except UnboundLocalError:
        #     return render(request, 'Home/login.html')
    if request.method == 'POST':
        print('hhhh')
        tk = request.POST['tk']
        mk = request.POST['mk']
        hash_object = hashlib.sha1(bytes(mk, 'utf-8'))
        mk = hash_object.hexdigest()
        try:
            d = TK(tk)
            print('xxxx')
            print(mk)
            print(d['MatKhau'])
            if d['TaiKhoan'] == tk and d['MatKhau'] == mk:
                print('yyyy')
                request.session['tk'] = tk
                request.session['mk'] = mk
                request.session['vtro'] = d['VaiTro']

                print("vtro la")
                print(request.session['vtro'])
                if d['VaiTro'] == 3:
                    try:
                        for i in request.session['cs_cart']:
                            if i['tk'] == request.session['tk']:
                                sl_ve = sum(a['SL'] for a in i['cart'])
                                break
                            else:
                                sl_ve = 0
                        return render(request, 'KH/index.html', {'sove': sl_ve, 'tk': request.session['tk']})
                    except KeyError:
                        return redirect('../../')
                else:
                    return redirect('../../')
        except UnboundLocalError:
            return redirect('../../')
    print(4)
    return render(request, 'Home/login.html')

def logout(request):
    if 'tk' in request.session and 'mk' in request.session:
        del request.session['tk']
        del request.session['mk']
        del request.session['vtro']
        print('logout')
        return render(request, 'Home/login.html')
    else:
        return redirect('../../customer/0')

def lichtrinhKH(request):
    # del request.session['cs_cart']
    # request.session['cs_cart'] = [{'MaLT': '61cbe6818b0d749f8e8d9bdb','SL': 1}]
    # print(request.session['cs_cart'])
    sl_ve = 0
    DVX = connection.connect_db()
    lt = DVX['LoTrinh']
    lt_ttr = lt.aggregate([
        {'$lookup':
             {'from': 'Tuyen_Tram',
              # 'let': {'n': {"$size": "$MaTuyen"}},
              'localField': 'MaTuyen',
              'foreignField': 'MaTuyen',
              # 'pipeline': [query10],
              'as': 'MaTuyen'}},
        {"$group": {
            "_id": "$_id",
            "TGXB": {"$first": "$TGXuatBen"},
            "TGDB": {"$first": "$TGDenBen"},
            "SoVe": {"$first": "$SoVe"},
            "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
            "Tram": {"$first": "$MaTuyen.MaTram"},
            "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
            "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
        }
        },
        {'$lookup':
             {'from': 'Tuyen',
              # 'let': {'n': {"$size": "$MaTuyen"}},
              'localField': 'MaTuyen',
              'foreignField': '_id',
              # 'pipeline': [query10],
              'as': 'MaTuyen'}},
        ])
    lt_ttr = list(lt_ttr)
    print(lt_ttr)
    # sl_ve = sum(i['cart']['SL'] for i in request.session['cs_cart'])
    if check_permission.check(request) == 3:
        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sl_ve = sum(a['SL'] for a in i['cart'])
                break
                print(sl_ve)
            else:
                sl_ve = 0
        return render(request, 'KH/lichtrinh.html', {'data': lt_ttr, 'sove': sl_ve, 'tk': request.session['tk']})
    else:
        return render(request, 'Home/lichtrinh.html', {'data': lt_ttr})




def ttcn(request):
    return render(request, 'KH/ttcn.html')


def vedadat(request):
    return render(request, 'KH/vedadat.html')

def giohang(request):
    if check_permission.check(request) == 3:
        ve = []
        for k in request.session['cs_cart']:
            print(k['tk'])
            if k['tk'] == request.session['tk']:
                print('......')
                print(k['cart'])
                print(request.session['tk'])
                for i in k['cart']:
                    print(i['MaLT'])
                    ve.append(ObjectId(i['MaLT']))
                    # print(ve)
                break
            else:
                ve = []
        print('ve...')
        print(ve)
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        data = lt.aggregate([
            {"$match": {
                "_id": {"$in": ve}
            }},
            {'$lookup':
                 {'from': 'Tuyen_Tram',
                  'localField': 'MaTuyen',
                  'foreignField': 'MaTuyen',
                  'as': 'MaTuyen'}},
            {"$group": {
                "_id": "$_id",
                "TGXB": {"$first": "$TGXuatBen"},
                "TGDB": {"$first": "$TGDenBen"},
                "SoVe": {"$first": "$SoVe"},
                "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
                "Tram": {"$first": "$MaTuyen.MaTram"},
                "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
                "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
            }
            },
            {'$lookup':
                 {'from': 'Tuyen',
                  'localField': 'MaTuyen',
                  'foreignField': '_id',
                  'as': 'MaTuyen'}},
        ])
        data = list(data)
        # print(ve)
        for i in data:
            for k in request.session['cs_cart']:
                if k['tk'] == request.session['tk']:
                    for a in k['cart']:
                        if str(i['_id']) == str(a['MaLT']):
                            i['SL'] = a['SL']

        print(data)
        print('skdfhdakflaifjl')
        print(request.session['cs_cart'])
        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sl_ve = sum(a['SL'] for a in i['cart'])
                break
            else:
                sl_ve = 0

        return render(request, 'KH/giohang.html', {'sove': sl_ve, 'data': data, 'tk': request.session['tk']})
    else:
        check_permission.del_session(request)
        return redirect('../../login')


@csrf_exempt
def update_cart(request):
    if request.is_ajax and request.method == 'POST':
        mlt = request.POST.get('mlt')
        sl = request.POST.get('sl')
        print(sl)
        print('-----cart v0------')
        print(request.session['cs_cart'])
        print('-----cart v0------')
        for k in request.session['cs_cart']:
            if k['tk'] == request.session['tk']:
                for i in k['cart']:
                    if mlt == str(i['MaLT']):
                        if int(sl) != 0:
                            i['SL'] = int(sl)
                        else:
                            k['cart'].remove(k)

        print('-----cart v1------')
        print(request.session['cs_cart'])
        print('-----cart v1------')
        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sl_ve = sum(a['SL'] for a in i['cart'])
                break
            else:
                sl_ve = 0
        return JsonResponse({'sove': sl_ve}, status=200)
    return JsonResponse({}, status=400)

def thanhtoan1(request):
    if check_permission.check(request) == 3:
        tongtien = 0
        data = []
        try:
            if request.method == 'POST':
                mlt = request.POST.getlist('mlt')
                sl = request.POST.getlist('soluong')
                tongtien = request.POST['tt']
                # tongtien = sum(int(i) for i in tongtien)
                print('tongtien: ' + str(tongtien))
                # sl ve trong cart
                # for i in range(0, len(mlt)):
                #     dict = {'MaLT': mlt[i], 'SL': int(sl[i])}
                #     cart.append(dict)
                # print('-------cart------')
                # print(cart)
                # print('-------cart------')
                for m in range(0, len(mlt)):
                    mlt[m] = ObjectId(mlt[m])
                DVX = connection.connect_db()
                lt = DVX['LoTrinh']
                data = lt.aggregate([
                    {"$match": {
                        "_id": {"$in": mlt}
                    }},
                    {'$lookup':
                         {'from': 'Tuyen_Tram',
                          'localField': 'MaTuyen',
                          'foreignField': 'MaTuyen',
                          'as': 'MaTuyen'}},
                    {"$group": {
                        "_id": "$_id",
                        "TGXB": {"$first": "$TGXuatBen"},
                        "TGDB": {"$first": "$TGDenBen"},
                        "SoVe": {"$first": "$SoVe"},
                        "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
                        "Tram": {"$first": "$MaTuyen.MaTram"},
                        "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
                        "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
                    }
                    },
                    {'$lookup':
                         {'from': 'Tuyen',
                          'localField': 'MaTuyen',
                          'foreignField': '_id',
                          'as': 'MaTuyen'}},
                ])
                data = list(data)
                for i in data:
                    for k in request.session['cs_cart']:
                        if k['tk'] == request.session['tk']:
                            for a in k['cart']:
                                if str(i['_id']) == str(a['MaLT']):
                                    i['SL'] = a['SL']

                # print('---------data--------')
                # print(data)
                # print('---------data--------')
                for h in data:
                    h['_id'] = str(h['_id'])
                request.session['cs_thanhtoan'] = data
                sl = sum(i['SL'] for i in request.session['cs_thanhtoan'])
            for i in request.session['cs_cart']:
                if i['tk'] == request.session['tk']:
                    sl_ve = sum(a['SL'] for a in i['cart'])
                    break
                else:
                    sl_ve = 0
            return render(request, 'KH/thanhtoan.html', {'data': data, 'tongtien': tongtien, 'sl': sl, 'sove': sl_ve, 'tk':request.session['tk']})
        except UnboundLocalError:
            return redirect("../customer/cart")
    else:
        check_permission.del_session(request)
        return redirect('../../login')

@csrf_exempt
# def thanhtoan_get(request):
#     tongtien = 0
#     sl = 0
#     if request.is_ajax and request.method == 'POST':
#         # tongtien = request.POST.get('tt')
#         cart = request.POST.get('dt')
#         # cart = json.loads(cart)
#         print('----------h--------')
#         print(cart)
#         print('----------h--------')
#         # mlt = []
#         # for k in cart:
#         #     mlt.append(ObjectId(k['MaVe']))
#         # print('-------MaLT-------')
#         # print(mlt)
#         # DVX = connection.connect_db()
#         # lt = DVX['LoTrinh']
#         # data = lt.aggregate([
#         #     {"$match": {
#         #         "_id": {"$in": mlt}
#         #     }},
#         #     {'$lookup':
#         #          {'from': 'Tuyen_Tram',
#         #           'localField': 'MaTuyen',
#         #           'foreignField': 'MaTuyen',
#         #           'as': 'MaTuyen'}},
#         #     {"$group": {
#         #         "_id": "$_id",
#         #         "TGXB": {"$first": "$TGXuatBen"},
#         #         "TGDB": {"$first": "$TGDenBen"},
#         #         "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
#         #         "Tram": {"$first": "$MaTuyen.MaTram"},
#         #         "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
#         #         "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
#         #     }
#         #     },
#         #     {'$lookup':
#         #          {'from': 'Tuyen',
#         #           'localField': 'MaTuyen',
#         #           'foreignField': '_id',
#         #           'as': 'MaTuyen'}},
#         # ])
#         # data = list(data)
#         # print(data)
#         # for i in cart:
#         #     for k in data:
#         #         if str(i['MaVe']) == str(k['_id']):
#         #             i['TGXB'] = k['TGXB']
#         #             i['TGDB'] = k['TGDB']
#         #             i['MaTuyen'] = k['MaTuyen']
#         #             i['Tram'] = k['Tram']
#         #             i['TramDau'] = k['TramDau']
#         #             i['TramCuoi'] = k['TramCuoi']
#         # print('----------cart v2-----------')
#         # print(cart)
#         # # for h in cart:
#         # #     h['MaVe'] = str(h['MaVe'])
#         # # request.session['cs_thanhtoan'] = cart
#         # return JsonResponse({}, status=200)
#         # return JsonResponse({'cart': cart}, status=200)
#     # else:
#     #     # sl = sum(i['SL'] for i in cart)
#     #     sl_ve = sum(i['SL'] for i in request.session['cs_cart'])
#     #     return render(request, 'KH/thanhtoan.html', {'data': request.session['cs_thanhtoan'], 'tongtien': tongtien, 'sove': sl_ve})


def check(request):
    # ket noi csdl
    DVX = connection.connect_db()
    try:
        medicine_1 = {
            "_id": "MR1",
            "common_name": "Paracetamol",
            "scientific_name": "",
            "available": "Y",
            "category": "fever"
        }

        thu = DVX["thu"]
        thu.insert_many([medicine_1])
        a = 'thanh cong'
    except BulkWriteError as bwe:
        # a = bwe.details['writeErrors']
         a = 'Khoa chinh khong duoc trung nhau'

    data = thu.find({"category": "fever"})
    for d in data:
        a = d["category"]
    request.session['fav_color'] = 'blue'
    return HttpResponse(request.session['fav_color'])

@csrf_exempt
def add_item(request, mlt):
    # del request.session['cs_cart']
    # request.session['cs_cart'] = [{'tk': 'bbb', 'cart': [{'MaLT': '61bdf3b03763d9f40aab3f4d', 'SL': 1}]}]
    if request.is_ajax and request.method == "POST":
        count = 0
        count1 = 0
        if 'cs_cart' in request.session:
            # print(request.session['cs_cart'])
            a = request.session['cs_cart']
            for k in a:
                # print('----')
                # print(k['cart'])
                print('d')
                if k['tk'] == request.session['tk']:
                    count1 = count1 + 1
                    for i in k['cart']:
                        if mlt == i['MaLT']:
                            i['SL'] = i['SL'] + 1
                            count = count + 1
                            print('fff')
                    if count == 0:
                        el = {'MaLT': mlt, 'SL': 1}
                        k['cart'].append(el)
                        print('dhskd')


            if count1 == 0:
                el = {'tk': request.session['tk'], 'cart': [{'MaLT': mlt, 'SL': 1}]}
                request.session['cs_cart'].append(el)
                print('elsls')
            print(request.session['cs_cart'])
        else:
            request.session['cs_cart'] = [{'tk': request.session['tk'], 'cart': [{'MaLT': mlt, 'SL': 1}]}]
        for k in a:
            if k['tk'] == request.session['tk']:
                sove = sum(i['SL'] for i in k['cart'])
                break
        # sove = 21
        return JsonResponse({"sove": sove}, status=200)
    return JsonResponse({}, status=400)

@csrf_exempt
def delete_item(request, mlt):
    if request.is_ajax and request.method == "POST":
        for k in request.session['cs_cart']:
            try:
                if k['tk'] == request.session['tk']:
                    for i in range(len(k['cart'])):
                        if mlt == str(k['cart'][i]['MaLT']):
                            print('iiiiii')
                            del k['cart'][i]
                            print('~~~~~~~~')
            except IndexError:
                break


        # for i in range(0, len(request.session['cs_cart'])):
        #   try:
        #     if mlt == request.session['cs_cart'][i]['MaLT']:
        #         del request.session['cs_cart'][i]
        #   except IndexError:
        #     break

        ve = []
        for k in request.session['cs_cart']:
            print(k['tk'])
            if k['tk'] == request.session['tk']:
                print('......')
                print(k['cart'])
                print(request.session['tk'])
                for i in k['cart']:
                    print(i['MaLT'])
                    ve.append(ObjectId(i['MaLT']))
                    # print(ve)
                break
            else:
                ve = []
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        data = lt.aggregate([
            {"$match": {
                "_id": {"$in": ve}
            }},
            {'$lookup':
                 {'from': 'Tuyen_Tram',
                  'localField': 'MaTuyen',
                  'foreignField': 'MaTuyen',
                  'as': 'MaTuyen'}},
            {"$group": {
                "_id": "$_id",
                "TGXB": {"$first": "$TGXuatBen"},
                "TGDB": {"$first": "$TGDenBen"},
                "SoVe": {"$first": "$SoVe"},
                "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
                "Tram": {"$first": "$MaTuyen.MaTram"},
                "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
                "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
            }
            },
            {'$lookup':
                 {'from': 'Tuyen',
                  'localField': 'MaTuyen',
                  'foreignField': '_id',
                  'as': 'MaTuyen'}},
        ])
        data = list(data)
        for i in data:
            for k in request.session['cs_cart']:
                if k['tk'] == request.session['tk']:
                    for a in k['cart']:
                        if str(i['_id']) == str(a['MaLT']):
                            i['SL'] = a['SL']

        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sove = sum(a['SL'] for a in i['cart'])
                break
            else:
                sove = 0
        return JsonResponse({"sove": sove}, status=200)
    return JsonResponse({}, status=400)

@csrf_exempt
def get_tb(request):
    print('GGGGGGGGGGG')
    ve = []
    for k in request.session['cs_cart']:
        print(k['tk'])
        if k['tk'] == request.session['tk']:
            print('......')
            print(k['cart'])
            print(request.session['tk'])
            for i in k['cart']:
                print(i['MaLT'])
                ve.append(ObjectId(i['MaLT']))
                # print(ve)
            break
        else:
            ve = []
    DVX = connection.connect_db()
    lt = DVX['LoTrinh']
    data = lt.aggregate([
        {"$match": {
            "_id": {"$in": ve}
        }},
        {'$lookup':
             {'from': 'Tuyen_Tram',
              'localField': 'MaTuyen',
              'foreignField': 'MaTuyen',
              'as': 'MaTuyen'}},
        {"$group": {
            "_id": "$_id",
            "TGXB": {"$first": "$TGXuatBen"},
            "TGDB": {"$first": "$TGDenBen"},
            "SoVe": {"$first": "$SoVe"},
            "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
            "Tram": {"$first": "$MaTuyen.MaTram"},
            "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
            "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
        }
        },
        {'$lookup':
             {'from': 'Tuyen',
              'localField': 'MaTuyen',
              'foreignField': '_id',
              'as': 'MaTuyen'}},
    ])
    data = list(data)
    # print(ve)
    for i in data:
        for k in request.session['cs_cart']:
            if k['tk'] == request.session['tk']:
                for a in k['cart']:
                    if str(i['_id']) == str(a['MaLT']):
                        i['SL'] = a['SL']
    print(data)
    for i in request.session['cs_cart']:
        if i['tk'] == request.session['tk']:
            sl_ve = sum(a['SL'] for a in i['cart'])
            break
        else:
            sl_ve = 0
    return render(request, 'KH/get_table.html', {'sove': sl_ve, 'data': data})

@csrf_exempt
def payment(request):
    DVX = connection.connect_db()
    lt = DVX['LoTrinh']
    dv = DVX['DatVe']
    dv_ct = DVX['DatVe_ChiTiet']
    if request.is_ajax and request.method == "POST":
        hoten = request.POST.get('ht')
        sdt = request.POST.get('SDT')
        email = request.POST.get('Email')
        tong = request.POST.get('Tong')
        data = request.session['cs_thanhtoan']
        print("hoten: {}".format(hoten))
        print("sdt: {}".format(sdt))
        print("mail: {}".format(email))
        query = {"MaKH": request.session['tk'], 'TTKH': {"HoTen":hoten,"SDT": sdt, "Email":email}, "TongTien": int(tong)}
        h = dv.insert_one(query).inserted_id
        for k in data:
            id = ObjectId(k['_id'])
            result = lt.find_one({"_id":id})
            query1 = {"MaDH": h, "Ve": id, "SL": k['SL']}
            sove = int(result['SoVe']) - int(k['SL'])
            print(request.session['cs_cart'])
            print(len(request.session['cs_cart']))
            for a in request.session['cs_cart']:
                try:
                    if a['tk'] == request.session['tk']:
                        for i in range(len(a['cart'])):
                            if a['cart'][i]["MaLT"] == k['_id']:
                                print('iiiiii')
                                del a['cart'][i]
                                print('~~~~~~~~')
                except IndexError:
                    break

            # for i in range(len(request.session['cs_cart'])):
            #     try:
            #         if request.session['cs_cart'][i]["MaLT"] == k['_id']:
            #             print(request.session['cs_cart'][i])
            #             del request.session['cs_cart'][i]
            #     except IndexError:
            #         break
            dv_ct.insert_one(query1)
            lt.update_one({"_id":id},{"$set":{"SoVe": sove}})
            # del request.session['cs_thanhtoan']
    # sl_ve = sum(i['SL'] for i in request.session['cs_cart'])
    return render(request, 'KH/tb_thanhtoan.html')

def demo(request):
    return render(request, 'KH/demo.html')

def ticket(request):
    if check_permission.check(request) == 3:
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        dv = DVX['DatVe']
        dv_ct = DVX['DatVe_ChiTiet']
        pipeline3 = [
            {'$lookup':
                 {'from': 'LoTrinh',
                  'localField': 'Ve',
                  'foreignField': '_id',
                  'as': 'ChiTietVe'}},
            {'$lookup':
                 {'from': 'Tuyen_Tram',
                  'localField': 'ChiTietVe.MaTuyen',
                  'foreignField': 'MaTuyen',
                  'as': 'TuyenXe'}},
            {'$lookup':
                 {'from': 'Tuyen',
                  'localField': 'TuyenXe.MaTuyen',
                  'foreignField': '_id',
                  'as': 'MaTuyen'}},
            {'$lookup':
                 {'from': 'DatVe',
                  'localField': 'MaDH',
                  'foreignField': '_id',
                  'as': 'TTDonHang'}},
            {'$project': {
                '_id': 0,
                'MaDH': 1,
                'Ve': 1,
                'ChiTietVe.TGXuatBen': 1,
                'ChiTietVe.TGDenBen': 1,
                'ChiTietVe.SoVe': 1,
                'SL': 1,
                'TTDonHang.MaKH': 1,
                'TTDonHang.TTKH': 1,
                'TTDonHang.TongTien': 1,
                'TuyenXe': 1,
                'MaTuyen.GiaVe': 1
            }},
            {"$addFields":
                {
                    "TramDau": {"$first": "$TuyenXe.MaTram.TenDuong"},
                    "TramCuoi": {"$last": "$TuyenXe.MaTram.TenDuong"},
                }
            },
            {"$match":
                {
                    "TTDonHang.MaKH": request.session['tk'],
                }
            },
            {"$group": {
                "_id": "$MaDH",
                "DonHang": {"$push": "$$ROOT"}
            }},

        ]

        data = dv_ct.aggregate(pipeline3)
        data = list(data)
        print(data)
        for i in request.session['cs_cart']:
            if i['tk'] == request.session['tk']:
                sove = sum(a['SL'] for a in i['cart'])
                break
            else:
                sove = 0
        return render(request, 'KH/vedadat.html', {'data': data, 'sove': sove, 'tk': request.session['tk']})
    else:
        check_permission.del_session(request)
        return redirect('../../login')


@csrf_exempt
def ticket_cancel(request):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M")
    print("Current Time =", current_time)
    if request.is_ajax and request.method == "POST":
        DVX = connection.connect_db()
        mdh = request.POST.get('madh')
        ve = request.POST.get('ve')
        sl = request.POST.get('sl')
        tgxb = request.POST.get('tgxb')
        dv_ct = DVX['DatVe_ChiTiet']
        kq = dv_ct.find_one({'MaDH': ObjectId(mdh), 'Ve': ObjectId(ve)})
        conlai = int(kq['SL']) - int(sl)
        now = datetime.now()
        now = now.strftime("%H:%M")
        tghuy = datetime.strptime(now, "%H:%M")
        print(tghuy)
        giohuy = tghuy.hour
        phuthuy = tghuy.minute

        tgxb = datetime.strptime(tgxb, "%H:%M")
        print(tgxb)
        gioxb = tgxb.hour
        phutxb = tgxb.minute
        tghuy = timedelta(hours=giohuy, minutes=phuthuy)
        tgxb = timedelta(hours=gioxb, minutes=phutxb)
        kq = tgxb - tghuy
        print(tgxb)
        print(tghuy)
        print(kq)
        if tghuy < tgxb and kq < timedelta(minutes=15):
            return JsonResponse({'tb': 'Thời gian hủy phải trước 15 phút xuất phát!'}, status=200)
        else:
            print("conlai" + str(conlai))
            if conlai == 0:
                print('aaaaa')
                dv_ct.remove({'MaDH': ObjectId(mdh), 'Ve': ObjectId(ve)})
            else:
                print('bbbb')
                dv_ct.update_one({'MaDH': ObjectId(mdh), 'Ve': ObjectId(ve)}, {"$set": {"SL": conlai}})

            dv_ct = dv_ct.find({"MaDH": ObjectId(mdh)}).count()
            print('----count v1-----')
            print('mdh' + str(mdh))
            print(str(dv_ct))
            if dv_ct == 0:
                DVX['DatVe'].remove({'_id': ObjectId(mdh)})
            return JsonResponse({'tb': 'Hủy vé thành công!'}, status=200)
    return JsonResponse({}, status=400)

# def thanhtoan(request):
#     tongtien = 0
#     sl = 0
#     if request.method == 'POST':
#         # tongtien = request.POST.get('tt')
#
#         # cart = thanhtoan_get
#         resp_dict = json.loads(cart)
#         # resp_dict['name']
#         # cart = json.loads(cart)
#         print('----------h--------')
#         print(resp_dict)
#         print('----------h--------')
#         # mlt = []
#         # for k in cart:
#         #     mlt.append(ObjectId(k['MaVe']))
#         # print('-------MaLT-------')
#         # print(mlt)
#         # DVX = connection.connect_db()
#         # lt = DVX['LoTrinh']
#         # data = lt.aggregate([
#         #     {"$match": {
#         #         "_id": {"$in": mlt}
#         #     }},
#         #     {'$lookup':
#         #          {'from': 'Tuyen_Tram',
#         #           'localField': 'MaTuyen',
#         #           'foreignField': 'MaTuyen',
#         #           'as': 'MaTuyen'}},
#         #     {"$group": {
#         #         "_id": "$_id",
#         #         "TGXB": {"$first": "$TGXuatBen"},
#         #         "TGDB": {"$first": "$TGDenBen"},
#         #         "MaTuyen": {"$first": {"$first": "$MaTuyen.MaTuyen"}},
#         #         "Tram": {"$first": "$MaTuyen.MaTram"},
#         #         "TramDau": {"$first": {"$first": "$MaTuyen.MaTram"}},
#         #         "TramCuoi": {"$last": {"$last": "$MaTuyen.MaTram"}}
#         #     }
#         #     },
#         #     {'$lookup':
#         #          {'from': 'Tuyen',
#         #           'localField': 'MaTuyen',
#         #           'foreignField': '_id',
#         #           'as': 'MaTuyen'}},
#         # ])
#         # data = list(data)
#         # print(data)
#         # for i in cart:
#         #     for k in data:
#         #         if str(i['MaVe']) == str(k['_id']):
#         #             i['TGXB'] = k['TGXB']
#         #             i['TGDB'] = k['TGDB']
#         #             i['MaTuyen'] = k['MaTuyen']
#         #             i['Tram'] = k['Tram']
#         #             i['TramDau'] = k['TramDau']
#         #             i['TramCuoi'] = k['TramCuoi']
#         # print('----------cart v2-----------')
#         # print(cart)
#         # # for h in cart:
#         # #     h['MaVe'] = str(h['MaVe'])
#         # # request.session['cs_thanhtoan'] = cart
#         return render(request, 'KH/thanhtoan.html')
#     else:
#         # sl = sum(i['SL'] for i in cart)
#         sl_ve = sum(i['SL'] for i in request.session['cs_cart'])
#         return render(request, 'KH/thanhtoan.html', {'data': request.session['cs_thanhtoan'], 'tongtien': tongtien, 'sove': sl_ve})

@csrf_exempt
def checkTK(request):
    if request.is_ajax and request.method == "POST":
        tk = request.POST.get('tk')
        vtr = request.POST.get('vtr')
        DVX = connection.connect_db()
        taikhoan = DVX['TaiKhoan']
        rlt = taikhoan.find({'TaiKhoan': tk}).count()
        print(str(rlt))
        if rlt > 0:
            kq = 1
        else:
            kq = 0
        return JsonResponse({'kq': kq}, status=200)
    return JsonResponse({}, status=400)
