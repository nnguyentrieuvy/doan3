import re

from bson import ObjectId
from django.shortcuts import render, redirect
from pymongo.errors import DuplicateKeyError
import check_permission
import connection
import hashlib
from json import dumps
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from datetime import datetime, timedelta


# Create your views here.
def qltd(request):
    return render(request, 'NVTD/qltd.html')


def ttsv(request):
    return render(request, 'NVTD/ttcn.html')

def doimk(request):
    return render(request, 'NVTD/doimk.html')


def themnv(request, vtr):
    if check_permission.check(request) == 0:
        if vtr == 1:
            return render(request, 'Admin/add.html')
        else:
            return render(request, 'Admin/add2.html')
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def sv_doimk(request):
    return render(request, 'NVSV/doimk.html')

def check_tel(tel_nb):
    gt = 0
    for i in tel_nb:
        nb = int(float(i))
        if nb in range(0, 9, 1):
            gt = gt + 0
        else:
            gt = gt + 1
    return gt


def add(request, vtr):
    if check_permission.check(request) == 0:
        DVX = connection.connect_db()
        nv = DVX["NhanVien"]
        tk = DVX["TaiKhoan"]
        try:

            if request.method == 'GET':
                mnv = request.GET['mnv']
                hoten = request.GET['hoten']
                gt = request.GET['gt']
                if gt == 'nam':
                    gt = 1
                else:
                    gt = 0
                ns = request.GET['ns']
                dc = request.GET['dc']
                sdt = request.GET['sdt']
                email = request.GET['email']
                hash_object = hashlib.sha1(bytes(mnv, 'utf-8'))
                mk = hash_object.hexdigest()
                if vtr == 1:
                    doc = {"_id": mnv, "HoTen": hoten, "GioiTinh": gt, "NgaySinh": ns, "DiaChi": dc,
                           "SDT": sdt, "Email": email, 'VaiTro': 1}
                    doc1 = {"TaiKhoan": mnv, "MatKhau": mk, 'VaiTro': 1}
                    nv.insert_one(doc)
                    tk.insert_one(doc1)
                else:
                    doc = {"_id": mnv, "HoTen": hoten, "GioiTinh": gt, "NgaySinh": ns, "DiaChi": dc,
                           "SDT": sdt, "Email": email, 'VaiTro': 2}
                    doc1 = {"TaiKhoan": mnv, "MatKhau": mk, 'VaiTro': 2}
                    nv.insert_one(doc)
                    tk.insert_one(doc1)
                return render(request, 'Admin/add.html')
        except DuplicateKeyError:
            return redirect('../' + str(vtr) + '/themnv')
        return render(request, 'Admin/add.html')
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def update(request, vtr, mnv):
    if check_permission.check(request) == 0:
        DVX = connection.connect_db()
        nv = DVX["NhanVien"]
        tk = DVX["TaiKhoan"]
        if vtr == 1:
            query = {'VaiTro': 1}
            title = 'Nhân viên tuyến đường'
        else:
            query = {'VaiTro': 2}
            title = 'Nhân viên soát vé'
        pipeline = [
            {
                "$match": query
            },
            {'$lookup':
                 {'from': 'NhanVien',
                  # 'let': {'n': {"$size": "$MaTuyen"}},
                  'localField': 'TaiKhoan',
                  'foreignField': '_id',
                  # 'pipeline': [query10],
                  'as': 'NhanVien'}},

        ]

        try:

            if request.method == 'GET':
                hoten = request.GET['hoten']
                gt = request.GET['gt']
                # gt = 'nam'
                if gt == 'nam':
                    gt = 1
                else:
                    gt = 0
                ns = request.GET['ns']
                dc = request.GET['dc']
                sdt = request.GET['sdt']
                email = request.GET['email']

                if vtr == 1:
                    doc = {"$set": {"HoTen": hoten, "GioiTinh": gt,
                                    "NgaySinh": ns,
                                    "DiaChi": dc, "SDT": sdt, "Email": email}}
                    nv.update_one({'_id': mnv}, doc)
                else:
                    doc = {"$set": {"HoTen": hoten, "GioiTinh": gt,
                                    "NgaySinh": ns,
                                    "DiaChi": dc, "SDT": sdt, "Email": email}}
                    nv.update_one({'_id': mnv}, doc)
                dt_one = nv.find_one({'_id': mnv})
                data = tk.aggregate(pipeline)
                return render(request, 'Admin/inf.html', {'dt': list(data), 'dt_one':dt_one, 'title': title})
        except DuplicateKeyError:
            return redirect('../mnv/capnhat/' + mnv)

        dt_one = nv.find_one({'_id': mnv})
        data = tk.aggregate(pipeline)
        print(data)
        return render(request, 'Admin/inf.html', {'dt': list(data), 'dt_one':dt_one, 'title': title})
    else:
        check_permission.del_session(request)
        return redirect('../admin')


def inf_upd(request, vtr):
    if check_permission.check(request) == 0:
        DVX = connection.connect_db()
        nv = DVX["NhanVien"]
        tk = DVX["TaiKhoan"]
        if vtr == 1:
            query = {'VaiTro': 1}
            title = 'Nhân viên tuyến đường'
        else:
            query = {'VaiTro': 2}
            title = 'Nhân viên soát vé'
        data = tk.aggregate([
            {
                "$match": query
            },
            {'$lookup':
                 {'from': 'NhanVien',
                  # 'let': {'n': {"$size": "$MaTuyen"}},
                  'localField': 'TaiKhoan',
                  'foreignField': '_id',
                  # 'pipeline': [query10],
                  'as': 'NhanVien'}},

            ])
        data = list(data)
        print(data)
        if vtr == 1:
            return render(request, 'Admin/inf_upd.html', {'dt': data, 'title': title, 'vtr': vtr})
        else:
            return render(request, 'Admin/inf_upd2.html', {'dt': data, 'title': title, 'vtr': vtr})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def inf(request, vtr, mnv):
    if check_permission.check(request) == 0:
        DVX = connection.connect_db()
        tk = DVX["TaiKhoan"]
        nv = DVX['NhanVien']
        if vtr == 1:
            query = {'VaiTro': 1}
            title = 'Nhân viên tuyến đường'
        else:
            query = {'VaiTro': 2}
            title = 'Nhân viên soát vé'
        data = tk.aggregate([
            {
                "$match": query
            },
            {'$lookup':
                 {'from': 'NhanVien',
                  # 'let': {'n': {"$size": "$MaTuyen"}},
                  'localField': 'TaiKhoan',
                  'foreignField': '_id',
                  # 'pipeline': [query10],
                  'as': 'NhanVien'}},

        ])
        data = list(data)
        # dt_one = nv.find_one(query1)
        dt_one = nv.find_one({'_id': mnv})
        return render(request, 'Admin/inf.html', {'dt': list(data), 'dt_one': dt_one, 'title': title})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def change_inf(request):
    DVX = connection.connect_db()
    nv = DVX["NhanVien"]
    if check_permission.check(request) == 1:
        tk = request.session['tk']
        data = nv.find_one({'_id': tk})
        return render(request, 'NVTD/ttcn.html', {'dt_one': data})
    elif check_permission.check(request) == 2:
        print(request.session['tk'])
        tk = request.session['tk']
        data = nv.find_one({'_id': tk})
        return render(request, 'NVSV/ttcn.html', {'dt_one': data})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def change(request):
    DVX = connection.connect_db()
    nv = DVX["NhanVien"]
    if check_permission.check(request) == 1:
        tk = request.session['tk']
        try:
            if request.method == 'GET':
                hoten = request.GET['hoten']
                gt = request.GET['gt']
                if gt == 'nam':
                    gt = 1
                else:
                    gt = 0
                ns = request.GET['ns']
                dc = request.GET['dc']
                sdt = request.GET['sdt']
                email = request.GET['email']
                doc = {"$set": {"_id": tk, "HoTen": hoten, "GioiTinh": gt, "NgaySinh": ns,
                                "DiaChi": dc, "SDT": sdt, "Email": email, "VaiTro": 1}}
                nv.update_one({'_id': tk}, doc)
        except DuplicateKeyError:
            return redirect('usr/information')
        data = nv.find_one({'_id': tk})
        return render(request, 'NVTD/ttcn.html', {'dt_one': data})
    if check_permission.check(request) == 2:
        tk = request.session['tk']
        print(tk)
        try:
            if request.method == 'GET':
                hoten = request.GET['hoten']
                gt = request.GET['gt']
                if gt == 'nam':
                    gt = 1
                else:
                    gt = 0
                ns = request.GET['ns']
                dc = request.GET['dc']
                sdt = request.GET['sdt']
                email = request.GET['email']
                doc = {"$set": {"_id": tk, "HoTen": hoten, "GioiTinh": gt, "NgaySinh": ns,
                                "DiaChi": dc, "SDT": sdt, "Email": email, "VaiTro": 2}}
                nv.update_one({'_id': tk}, doc)
        except DuplicateKeyError:
            return redirect('usr/information')
        data = nv.find_one({'_id': tk})
        print(data['_id'])
        return render(request, 'NVSV/ttcn.html', {'dt_one': data})
    else:
        check_permission.del_session(request)
        return redirect('../admin')


def change_password(request):
    DVX = connection.connect_db()
    tk = DVX["TaiKhoan"]
    mnv = request.session['tk']
    m = ''
    color = 'green'
    if check_permission.check(request) == 0:
        try:
            if request.method == 'POST':
                mkcu = request.POST['mkcu']
                mkcu = hashlib.sha1(bytes(mkcu, 'utf-8'))
                mkcu = mkcu.hexdigest()

                mkmoi = request.POST['mkmoi']
                mkmoi = hashlib.sha1(bytes(mkmoi, 'utf-8'))
                mkmoi = mkmoi.hexdigest()

                xnmk = request.POST['xnmk']
                xnmk = hashlib.sha1(bytes(xnmk, 'utf-8'))
                xnmk = xnmk.hexdigest()
                if mkcu == request.session['mk']:
                    if mkmoi == xnmk:
                        doc = {"$set": {"TaiKhoan": mnv, "MatKhau": mkmoi, "VaiTro": 0}}
                        tk.update_one({'TaiKhoan': mnv}, doc)
                        m = 'Thao tác thành công!'
                    else:
                        m = 'Mật khẩu mới và mật khẩu xác nhận khác nhau!'
                        color = 'red'
                else:
                    m = 'Mật khẩu không đúng!'
                    color = 'red'
        except DuplicateKeyError:
            return redirect('usr/changepassword')
        return render(request, 'Admin/doimk.html', {'m':m, 'color': color})

    if check_permission.check(request) == 1:
        try:
            if request.method == 'POST':
                mkcu = request.POST['mkcu']
                mkcu = hashlib.sha1(bytes(mkcu, 'utf-8'))
                mkcu = mkcu.hexdigest()

                mkmoi = request.POST['mkmoi']
                mkmoi = hashlib.sha1(bytes(mkmoi, 'utf-8'))
                mkmoi = mkmoi.hexdigest()

                xnmk = request.POST['xnmk']
                xnmk = hashlib.sha1(bytes(xnmk, 'utf-8'))
                xnmk = xnmk.hexdigest()
                if mkcu == request.session['mk']:
                    if mkmoi == xnmk:
                        doc = {"$set": {"TaiKhoan": mnv, "MatKhau": mkmoi, "VaiTro": 1}}
                        tk.update_one({'TaiKhoan': mnv}, doc)
                        m = 'Thao tác thành công!'
                    else:
                        m = 'Mật khẩu mới và mật khẩu xác nhận khác nhau!'
                        color = 'red'
                else:
                    m = 'Mật khẩu không đúng!'
                    color = 'red'
        except DuplicateKeyError:
            return redirect('usr/changepassword')
        return render(request, 'NVTD/doimk.html', {'m':m, 'color': color})
    if check_permission.check(request) == 2:
        try:
            if request.method == 'POST':
                mkcu = request.POST['mkcu']
                mkcu = hashlib.sha1(bytes(mkcu, 'utf-8'))
                mkcu = mkcu.hexdigest()

                mkmoi = request.POST['mkmoi']
                mkmoi = hashlib.sha1(bytes(mkmoi, 'utf-8'))
                mkmoi = mkmoi.hexdigest()

                xnmk = request.POST['xnmk']
                xnmk = hashlib.sha1(bytes(xnmk, 'utf-8'))
                xnmk = xnmk.hexdigest()
                if mkcu == request.session['mk']:
                    if mkmoi == xnmk:
                        doc = {"$set": {"TaiKhoan": mnv, "MatKhau": mkmoi, "VaiTro": 2}}
                        tk.update_one({'TaiKhoan': mnv}, doc)
                        m = 'Thao tác thành công!'
                    else:
                        m = 'Mật khẩu mới và mật khẩu xác nhận khác nhau!'
                        color = 'red'
                else:
                    m = 'Mật khẩu không đúng!'
                    color = 'red'
        except DuplicateKeyError:
            return redirect('usr/changepassword')
        return render(request, 'NVSV/doimk.html', {'m': m, 'color': color})
    else:
        check_permission.del_session(request)
        return redirect('../admin')


def city_route(request):
    if check_permission.check(request) == 1:
        return render(request, 'NVTD/td.html')
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def city_route_add(request):
    if check_permission.check(request) == 1:
        if request.method == 'GET':
            try:
                DVX = connection.connect_db()
                td = DVX['TuyenDuong']
                maduong = request.GET['maduong']
                tenduong = request.GET['tenduong']
                query = {"_id": maduong, "TenDuong": tenduong}
                td.insert_one(query)
                print(maduong)
                print(tenduong)
            except DuplicateKeyError:
                return redirect('../city_route/')
        return render(request, 'NVTD/td.html')
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def city_route_inf_upd(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        td = DVX['TuyenDuong']
        data = td.find()
        print(type(data))
        return render(request, 'NVTD/td_inf.html', {'data': data})
    else:
        check_permission.del_session(request)
        return redirect('../admin')


def city_route_change(request, md):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        td = DVX['TuyenDuong']
        data = td.find()
        dt = td.find_one({"_id": md})
        return render(request, 'NVTD/td_update.html', {'dt': dt, 'data': data, 'dt': dt})
    else:
        check_permission.del_session(request)
        return redirect('../admin')


def city_route_update(request, md):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        td = DVX['TuyenDuong']
        if request.method == 'GET':
            tenduong = request.GET['tenduong']
            doc = {"$set": {"TenDuong": tenduong}}
            td.update_one({'_id': md}, doc)
        data = td.find()
        dt = td.find_one({"_id": md})
        return render(request, 'NVTD/td_update.html', {'dt': dt, 'data': data})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def route(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        td = DVX['TuyenDuong']
        t = DVX['Tuyen']
        tuyen = DVX['tuyen']
        t_td = DVX['Tuyen_TD']
        ds_tuyen = t.find({})
        ds_duong = td.find({}, {"TenDuong": 1, "_id": 0})

        pipeline = [{'$lookup':
                          {'from': 'Tuyen_TD',
                           'localField': '_id',
                           'foreignField': 'MaTuyen',
                           'as': 'MaTD'}},
                     # {'$match': {'MaTuyen.MaTuyen': mt}}
                     # {'$project': {'MaTram.TenDuong': 1}}
                     ]

        pipeline2 = [{'$lookup':
                          {'from': "Tuyen_Tram",
                           'localField': "_id",
                           'foreignField': "MaTuyen",
                           'as': "MT"}},
                           {'$project': {'MT': 1}},
                           # {'$unwind': "$MT"},
                           # {'$unwind': "$TenDuong"}
                     ]

        # t1 = tuyen.aggregate(pipeline)
        # t1 = list(t1)
        dt_ct = t.aggregate(pipeline2)
        dt_ct = list(dt_ct)
        print(dt_ct)
        return render(request, 'NVTD/tx.html', {'ds_duong': ds_duong, 'ds_tuyen': ds_tuyen, 'dt_ct':dt_ct})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def route_selected(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        td = DVX['TuyenDuong']
        ds_duong = td.find({}, {"TenDuong": 1, "_id": 0})
        return render(request, 'NVTD/tx_chonma.html', {'ds_duong': ds_duong})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def route_sel_add(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        td = DVX['TuyenDuong']
        tx = DVX['Tuyen']
        tuyen_tram = DVX['Tuyen_Tram']
        lt = DVX['LoTrinh']
        tong = int(request.GET['laygt']) + 1
        print('tong'+str(tong))
        ds_duong = td.find({}, {"TenDuong": 1, "_id": 0})
        sel = 0
        if request.method == 'GET':
            matuyen = request.GET['mt']
            giave = request.GET['giave']
            tgxb = request.GET['tgxb']
            tgdb = request.GET['tgdb']
            # query_tx = {"_id": matuyen, "GiaVe": giave}
            query_tx = {"_id": matuyen, "GiaVe": int(giave)}
            query_lt = {"TGXuatBen": tgxb, "TGDenBen": tgdb, "MaTuyen": matuyen}
            for x in range(1, int(tong) + 1):
                try:
                    duong = request.GET[str(x)]
                    check = True
                    if duong != '0':
                       print(duong)
                       sel = sel + 1
                except MultiValueDictKeyError:
                    check = False
                    # tuyen xe phai co tram cuoi
                    return redirect('../../bus_route')
            if check == True and sel > 1:
                try:
                    tx.insert_one(query_tx)
                    lt.insert_one(query_lt)
                    for x in range(1, int(tong) + 1):
                        duong = request.GET[str(x)]
                        print(2222)
                        print(duong)
                        if duong != 0:
                            print('ten duong != 0 la {}'.format(duong))
                            tt = x
                            matram = td.find_one({"TenDuong": duong})
                            query_t_tr = {"MaTuyen": matuyen, "MaTram": matram, "tt": tt}
                            tuyen_tram.insert_one(query_t_tr)
                        else:
                            return redirect('../../bus_route')
                except DuplicateKeyError:
                    return redirect('../../bus_route')
            else:
                # cac tuyen duong phai duoc chon
                return redirect('../../bus_route')

        return render(request, 'NVTD/tx_chonma.html', {'ds_duong': ds_duong})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def route_information(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        # t_tr = DVX['Tuyen_Tram']
        pipeline = [{'$lookup':
                         {'from': 'Tuyen_Tram',
                          'localField': 'MaTuyen',
                          'foreignField': 'MaTuyen',
                          'as': 'MaTuyen'}},
                    # {'$match': {'MaTuyen.MaTuyen': 'NTMT'}}
                    ]

        data = lt.aggregate(pipeline)
        data = list(data)
        return render(request, 'NVTD/tx_upd.html', {'data': data})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def route_chitiet(request, mt):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        # t_tr = DVX['Tuyen_Tram']
        pipeline = [{'$lookup':
                         {'from': 'Tuyen_Tram',
                          'localField': 'MaTuyen',
                          'foreignField': 'MaTuyen',
                          'as': 'MaTuyen'}},
                    # {'$match': {'MaTuyen.MaTuyen': 'NTMT'}}
                    ]

        # pipeline2 = [{'$lookup':
        #                  {'from': 'Tuyen_Tram',
        #                   'localField': 'MaTuyen',
        #                   'foreignField': 'MaTuyen',
        #                   'as': 'MaTuyen'}},
        #             {'$match': {'MaTuyen.MaTuyen': mt }}
        #             ]

        pipeline3 = [{'$lookup':
                          {'from': 'Tuyen_Tram',
                           'localField': 'MaTuyen',
                           'foreignField': 'MaTuyen',
                           'as': 'MaTuyen'}},
                     {'$match': {'_id': ObjectId(mt)}}
                     ]

        data = lt.aggregate(pipeline)
        data = list(data)
        td = DVX['TuyenDuong']
        t = DVX['Tuyen']
        # dt_ct = lt.aggregate(pipeline2)
        # dt_ct = list(dt_ct)
        # # print(dt_ct)

        lt_t = lt.aggregate(pipeline3)
        lt_t = list(lt_t)
        # print(lt_t)
        ds_duong = td.find({}, {"TenDuong": 1, "_id": 0})
        ds_tuyen = t.find({})
        ds_duong = list(ds_duong)
        return render(request, 'NVTD/tx_upd.html',
                      {'data': data, 'ds_duong': ds_duong, 'ds_tuyen': ds_tuyen, 'lt_t': lt_t, 'mlt':mt})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def bus_route(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        t = DVX['Tuyen']
        pipeline = [{'$lookup':
                         {'from': 'Tuyen_Tram',
                          'localField': '_id',
                          'foreignField': 'MaTuyen',
                          'as': 'MaTuyen'}},
                    # {'$match': {'MaTuyen.MaTuyen': 'NTMT'}}
                    ]
        data = t.aggregate(pipeline)
        data = list(data)
        print(data)
        return render(request, 'NVTD/ds_tuyen.html', {'data': data})
    if check_permission.check(request) == 2:
        return render(request, 'NVSV/lichtrinh.html')
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def route_add(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        if request.method == 'GET':
            matuyen = request.GET['mt']
            tgxb = request.GET['tgxb']
            tgdb = request.GET['tgdb']
            query_lt = {"TGXuatBen": tgxb, "TGDenBen": tgdb, "MaTuyen": matuyen, "SoVe": 20}
            lt.insert_one(query_lt)
        return render(request, 'NVTD/tx.html')
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def bus_route_chitiet(request, mt):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        td = DVX['TuyenDuong']
        t = DVX['Tuyen']
        pipeline = [{'$lookup':
                         {'from': 'Tuyen_Tram',
                          'localField': '_id',
                          'foreignField': 'MaTuyen',
                          'as': 'MaTuyen'}},
                    # {'$match': {'MaTuyen.MaTuyen': 'NTMT'}}
                    ]
        data = t.aggregate(pipeline)
        data = list(data)
        print(data)

        pipeline2 = [{'$lookup':
                          {'from': 'Tuyen_Tram',
                           'localField': '_id',
                           'foreignField': 'MaTuyen',
                           'as': 'MaTuyen'}},
                     {'$match': {'MaTuyen.MaTuyen': mt}}
                     ]
        dt_ct = t.aggregate(pipeline2)
        dt_ct = list(dt_ct)

        ds_duong = td.find({}, {"TenDuong": 1, "_id": 0})
        ds_tuyen = t.find({})
        ds_duong = list(ds_duong)
        return render(request, 'NVTD/ds_tuyen.html',
                      {'data': data, 'ds_duong': ds_duong, 'ds_tuyen': ds_tuyen, 'dt_ct': dt_ct})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def bus_route_upd(request, mt):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        td = DVX['TuyenDuong']
        t = DVX['Tuyen']
        if request.method == 'GET':
            giave = request.GET['giave']
            query = {"$set": {"GiaVe": int(giave)}}
            print(10000)
            t.update_one({"_id": mt}, query)

        pipeline = [{'$lookup':
                         {'from': 'Tuyen_Tram',
                          'localField': '_id',
                          'foreignField': 'MaTuyen',
                          'as': 'MaTuyen'}},
                    # {'$match': {'MaTuyen.MaTuyen': 'NTMT'}}
                    ]
        data = t.aggregate(pipeline)
        data = list(data)
        print(data)

        pipeline2 = [{'$lookup':
                          {'from': 'Tuyen_Tram',
                           'localField': '_id',
                           'foreignField': 'MaTuyen',
                           'as': 'MaTuyen'}},
                     {'$match': {'MaTuyen.MaTuyen': mt}}
                     ]
        dt_ct = t.aggregate(pipeline2)
        dt_ct = list(dt_ct)

        ds_duong = td.find({}, {"TenDuong": 1, "_id": 0})
        ds_tuyen = t.find({})
        ds_duong = list(ds_duong)

        return render(request, 'NVTD/ds_tuyen.html',
                      {'data': data, 'ds_duong': ds_duong, 'ds_tuyen': ds_tuyen, 'dt_ct': dt_ct, 'mt': mt})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def route_inf(request, mt):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        t = DVX['Tuyen']
        # t_tr = DVX['Tuyen_Tram']
        pipeline = [{'$lookup':
                         {'from': 'Tuyen_Tram',
                          'localField': 'MaTuyen',
                          'foreignField': 'MaTuyen',
                          'as': 'MaTuyen'}},
                    {'$match': {'MaTuyen.MaTuyen': mt}}
                    ]
        ds_tuyen = t.find({})
        ds_tuyen = list(ds_tuyen)
        data = lt.aggregate(pipeline)
        data = list(data)
        print(ds_tuyen)
        return render(request, 'NVTD/tx_upd.html', {'data': data, 'ds_tuyen': ds_tuyen})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def route_upd(request, mt):
    if check_permission.check(request) == 1:

        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        if request.method == 'GET':
            tgxb = request.GET['tgxb']
            tgdb = request.GET['tgdb']
            vecosan = request.GET['vecosan']
            print(mt)
            query = {"$set": {"TGXuatBen": tgxb, "TGDenBen": tgdb, "SoVe":vecosan}}
            lt.update_one({"_id": ObjectId(mt)}, query)

            print(10000)

        pipeline = [{'$lookup':
                         {'from': 'Tuyen_Tram',
                          'localField': 'MaTuyen',
                          'foreignField': 'MaTuyen',
                          'as': 'MaTuyen'}},
                    ]

        pipeline3 = [{'$lookup':
                          {'from': 'Tuyen_Tram',
                           'localField': 'MaTuyen',
                           'foreignField': 'MaTuyen',
                           'as': 'MaTuyen'}},
                     {'$match': {'_id': ObjectId(mt)}}
                     ]

        data = lt.aggregate(pipeline)
        data = list(data)
        td = DVX['TuyenDuong']
        t = DVX['Tuyen']

        lt_t = lt.aggregate(pipeline3)
        lt_t = list(lt_t)
        # print(lt_t)
        ds_duong = td.find({}, {"TenDuong": 1, "_id": 0})
        ds_tuyen = t.find({})
        ds_duong = list(ds_duong)
        return render(request, 'NVTD/tx_upd.html',
                      {'data': data, 'ds_duong': ds_duong, 'ds_tuyen': ds_tuyen, 'mlt':mt, 'lt_t': lt_t})
    else:
        check_permission.del_session(request)
        return redirect('../admin')


def nvsv_search(request):
    if check_permission.check(request) == 2:
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        tram = request.GET['tram']
        tr = tram
        tgxb = request.GET['tgxb']
        print("hhjkhkjk" + tgxb)
        tgdb = request.GET['tgdb']

        if tgxb == "":
            tgxb = ["$ne", ""]
        else:
            tgxb = [tgxb]
            tgxb = ["$in", tgxb]

        if tgdb == "":
            tgdb = ["$ne", ""]
        else:
            tgdb = [tgdb]
            tgdb = ["$in", tgdb]

        if tram == "":
            tram = ["$ne", ""]
        else:
            tram = [tram]
            tram = ["$in", tram]

        pipeline = [{'$lookup':
                         {'from': 'Tuyen_Tram',
                          # 'let': {'n': {"$size": "$MaTuyen"}},
                          'localField': 'MaTuyen',
                          'foreignField': 'MaTuyen',
                          # 'pipeline': [query10],
                          'as': 'MaTuyen'}},
                    {"$match":
                        {
                            "TGXuatBen": {tgxb[0]: tgxb[1]},
                            "TGDenBen": {tgdb[0]: tgdb[1]},
                            "MaTuyen.MaTram.TenDuong": {tram[0]: tram[1]}
                        }
                    }
                    ]

        lt_ttr = lt.aggregate(pipeline)
        lt_ttr = list(lt_ttr)
        print(lt_ttr)
        return render(request, 'NVSV/lichtrinh.html', {'data': lt_ttr, 'tram': tr})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def ticket(request):
    return render(request, 'NVSV/vedadat.html')

def ticket_search(request):
    if check_permission.check(request) == 2:
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        # dv = DVX['DatVe']
        dv_ct = DVX['DatVe_ChiTiet']
        tram = request.GET['tram']
        tr = tram
        tgxb = request.GET['tgxb']
        tgdb = request.GET['tgdb']
        sdt = request.GET['sdt']

        if tgxb == "":
            tgxb = ["$ne", ""]
        else:
            tgxb = [tgxb]
            tgxb = ["$in", tgxb]

        if tgdb == "":
            tgdb = ["$ne", ""]
        else:
            tgdb = [tgdb]
            tgdb = ["$in", tgdb]

        if tram == "":
            tram = ["$ne", ""]
        else:
            tram = [tram]
            tram = ["$in", tram]

        if sdt == "":
            sdt = ["$ne", ""]
        else:
            sdt = [sdt]
            sdt = ["$in", sdt]


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
            {"$match":
                {
                    "ChiTietVe.TGXuatBen": {tgxb[0]: tgxb[1]},
                    "ChiTietVe.TGDenBen": {tgdb[0]: tgdb[1]},
                    "TuyenXe": {
                        "$elemMatch": {
                            "MaTram.TenDuong": {tram[0]: tram[1]}
                            # "MaTram.TenDuong": {'$regex': '^N', '$options': 'i'}
                            # "MaTram.TenDuong": {"$in": [re.compile(".*g*.")]}
                            # "MaTram.TenDuong": {"$in": [re.compile(".N*g*.")]}
                            # "MaTram.TenDuong": {"$in": [re.compile(".(N|n)gu.")]}
                        }
                    }
                }
            },
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
            }},
            {"$match":
                {
                    "TTDonHang.TTKH.SDT": {sdt[0]: sdt[1]}
                }
            }
            # {"regexMatch":
            #     {
            #         "input": "TTDonHang.TTKH.SDT", "regex": {sdt[0]: sdt[1]},
            #     }
            # }
            ]

        dh = dv_ct.aggregate(pipeline3)
        dh = list(dh)
        print('chay ticket_search')
        print('---dat ve---')
        print(dh)
        print('---dat ve---')
        return render(request, 'NVSV/vedadat.html', {'data': dh, 'tram': tr})
    else:
        check_permission.del_session(request)
        return redirect('../admin')


@csrf_exempt
def cancel(request):
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M")
    print("Current Time =", current_time)
    if request.is_ajax and request.method == "POST":
        DVX = connection.connect_db()
        mdh = request.POST.get('madh')
        ve = request.POST.get('ve')
        sl = request.POST.get('sl')
        tgxb = request.POST.get('tgxb')
        # print(tgxb)
        dv = DVX['DatVe']
        dv_ct = DVX['DatVe_ChiTiet']
        # pipeline = [
        #     # {'$lookup':
        #     #     {'from': 'DatVe_ChiTiet',
        #     #      'localField': '_id',
        #     #      'foreignField': 'MaDH',
        #     #      'as': 'TTDonHang'}
        #     # },
        #     {"$match":
        #         {
        #             "_id": ObjectId(mdh)
        #         }
        #     },
        #     # {'$project': {
        #     #     'MaDH': 1,
        #     #     'TTKH': 1,
        #     #     'TongTien': 1,
        #     #     'TTDonHang.Ve': 1,
        #     #     'TTDonHang.SL': 1
        #     # }
        #     # },
        #     {'$count': "_id"}
        #     # {"$addField": {"SoLoaiVe": {"$count": "TTDonHang"}}}
        # ]
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


def bus(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        pipeline2 = [{'$lookup':
                          {'from': "Tuyen_Tram",
                           'localField': "MaTuyen",
                           'foreignField': "MaTuyen",
                           'as': "MT"}},
                     ]
        dt_ct = lt.aggregate(pipeline2)
        dt_ct = list(dt_ct)
        print(dt_ct)
        return render(request, 'NVTD/bus_add.html', {'dt_ct': dt_ct})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def ds_bus(request):
    return render(request, 'NVTD/bus_update.html', )

def bus_add(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        lt = DVX['LoTrinh']
        pipeline2 = [{'$lookup':
                          {'from': "Tuyen_Tram",
                           'localField': "MaTuyen",
                           'foreignField': "MaTuyen",
                           'as': "MT"}},
                     ]
        dt_ct = lt.aggregate(pipeline2)
        if request.method == 'GET':
            DVX = connection.connect_db()
            buss = DVX['XeBuyt']
            mlt = request.GET['mlt']
            bs = request.GET['bs']
            mx = request.GET['mx']
            query = {"_id": mx, "MaLoTrinh": mlt, "BienSo": bs}
            buss.insert_one(query)
        #     print(mlt)
        #     print(bs)
        #     print(mx)
        dt_ct = list(dt_ct)
        print(dt_ct)
        return render(request, 'NVTD/bus_add.html', {'dt_ct': dt_ct})
    else:
        check_permission.del_session(request)
        return redirect('../admin')


def bus_update(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        nv = DVX["XeBuyt"]
        data = nv.find()
        dt_one = nv.find_one()
        print(data)
        # try:
        #     if request.method == 'GET':
        #         mx = request.GET['mx']
        #         mlt = request.GET['mlt']
        #         bs = request.GET['bs']
        #         doc = {"$set": {"_id": mx, "MaLoTrinh": mlt, "BienSo": bs}}
        #         nv.update_one(doc)
        #     return render(request,'NVTD/bus_add.html', {'dt': list(data), 'dt_one': dt_one})
        # except DuplicateKeyError:
        return render(request,'NVTD/bus_update.html', {'dt': list(data), 'dt_one': dt_one})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

def bus_infor(request):
    if check_permission.check(request) == 1:
        DVX = connection.connect_db()
        b = DVX['XeBuyt']
        pipeline2 = [{'$lookup':
                          {'from': "LoTrinh",
                           'localField': "MaLoTrinh",
                           'foreignField': "_id",
                           'as': "LT"}}
                     ]
        dt = b.aggregate(pipeline2)
        dt = list(dt)
        print(dt)
        return render(request, 'NVTD/bus_inf.html', {'dt': dt})
    else:
        check_permission.del_session(request)
        return redirect('../admin')

@csrf_exempt
def checkMTD(request):
    if request.is_ajax and request.method == "POST":
        mtd = request.POST.get('mtd')
        DVX = connection.connect_db()
        td = DVX['TuyenDuong']
        rlt = td.find({'_id': mtd}).count()
        print(str(rlt))
        if rlt > 0:
            kq = 1
        else:
            kq = 0
        return JsonResponse({'kq': kq}, status=200)
    return JsonResponse({}, status=400)