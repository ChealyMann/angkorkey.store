import os
import sys
import io

# Ensure root folder is in path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import app
from extensions import db
from models import Category, Brand, Product, User
from models.Voucher import Voucher
from models.Promotion import Promotion

# Configure testing app
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

client = app.test_client()

def test_crud():
    print("=" * 60)
    print("STARTING ALL MOBILE PORTAL CRUD INTEGRATION TESTS")
    print("=" * 60)
    
    with app.app_context():
        # Find or create default admin user
        admin = User.query.filter_by(username="chealy").first()
        if not admin:
            from werkzeug.security import generate_password_hash
            admin = User(username="chealy", password=generate_password_hash("zxnmtt123789"))
            db.session.add(admin)
            db.session.commit()
        
        # Simulate active session login
        with client.session_transaction() as sess:
            sess['user_id'] = admin.id

        # Clean up any leftover test data first
        Category.query.filter(Category.name.like('Test Cat%')).delete(synchronize_session=False)
        Brand.query.filter(Brand.name.like('Test Brand%')).delete(synchronize_session=False)
        Product.query.filter(Product.name.like('Test Product%')).delete(synchronize_session=False)
        User.query.filter(User.username.like('testusermobile%')).delete(synchronize_session=False)
        Promotion.query.filter(Promotion.title.like('Test Promo%')).delete(synchronize_session=False)
        Voucher.query.filter(Voucher.code.like('TESTVOUCH%')).delete(synchronize_session=False)
        db.session.commit()

        # ------------------------------------------------------------
        # Test 1: Category CRUD
        # ------------------------------------------------------------
        print("\n[1/6] Testing Category CRUD...")
        # Create
        res = client.post('/admin/mobile/category/add', data={
            'name': 'Test Category Mobile',
            'desc': 'Testing description for category',
            'status': 'true'
        }, follow_redirects=True)
        assert res.status_code == 200, f"Category Add page failed with status {res.status_code}"
        
        cat = Category.query.filter_by(name='Test Category Mobile').first()
        assert cat is not None, "Category not found in Database"
        print(" -> Category Creation: PASS")

        # Read
        res = client.get('/admin/mobile/category')
        assert res.status_code == 200, "Category List page failed"
        assert b'Test Category Mobile' in res.data, "Created category name not in response body"
        print(" -> Category Listing & Retrieval: PASS")

        # Update
        res = client.post(f'/admin/mobile/category/edit/{cat.id}', data={
            'name': 'Test Cat Mobile Edited',
            'desc': 'Updated testing description',
            'status': 'false'
        }, follow_redirects=True)
        assert res.status_code == 200, "Category Edit failed"
        
        cat = Category.query.get(cat.id)
        if cat.name != 'Test Cat Mobile Edited':
            print("--- Category edit failed! Dumping page response for diagnostic ---")
            print(res.data.decode('utf-8', errors='ignore'))
            print("------------------------------------------------------------------")
        assert cat.name == 'Test Cat Mobile Edited', "Category edit name change not in database"
        assert cat.status == 'false', "Category edit status change not in database"
        print(" -> Category Update: PASS")

        # ------------------------------------------------------------
        # Test 2: Brand CRUD
        # ------------------------------------------------------------
        print("\n[2/6] Testing Brand CRUD...")
        # Create
        res = client.post('/admin/mobile/brand/add', data={
            'name': 'Test Brand Mobile',
            'desc': 'Brand testing description',
            'status': 'true'
        }, follow_redirects=True)
        assert res.status_code == 200, "Brand Add failed"
        
        brand = Brand.query.filter_by(name='Test Brand Mobile').first()
        assert brand is not None, "Brand not found in Database"
        print(" -> Brand Creation: PASS")

        # Read
        res = client.get('/admin/mobile/brand')
        assert res.status_code == 200, "Brand List page failed"
        assert b'Test Brand Mobile' in res.data, "Created brand name not in response"
        print(" -> Brand Listing & Retrieval: PASS")

        # Update
        res = client.post(f'/admin/mobile/brand/edit/{brand.id}', data={
            'name': 'Test Brand Mobile Edited',
            'desc': 'Updated brand desc',
            'status': 'true'
        }, follow_redirects=True)
        assert res.status_code == 200, "Brand Edit failed"
        
        brand = Brand.query.get(brand.id)
        assert brand.name == 'Test Brand Mobile Edited', "Brand edit not in database"
        print(" -> Brand Update: PASS")

        # ------------------------------------------------------------
        # Test 3: Product CRUD
        # ------------------------------------------------------------
        print("\n[3/6] Testing Product CRUD...")
        # Create
        res = client.post('/admin/mobile/product/add', data={
            'name': 'Test Product Mobile',
            'desc': '<p>Html desc</p>',
            'category': str(cat.id),
            'brand': str(brand.id),
            'price': 15.99,
            'cost': 10.00,
            'old_price': 20.00,
            'status': 'true'
        }, follow_redirects=True)
        assert res.status_code == 200, "Product Add failed"
        
        prod = Product.query.filter_by(name='Test Product Mobile').first()
        if prod is None:
            print("--- Product creation failed! Dumping page response for diagnostic ---")
            print(res.data.decode('utf-8', errors='ignore'))
            print("-------------------------------------------------------------------")
        assert prod is not None, "Product not found in Database"
        print(" -> Product Creation: PASS")

        # Read
        res = client.get('/admin/mobile/product')
        assert res.status_code == 200, "Product list page failed"
        print(" -> Product Listing & Retrieval: PASS")

        # Update
        res = client.post(f'/admin/mobile/product/edit/{prod.id}', data={
            'name': 'Test Product Mobile Edited',
            'desc': '<p>Html desc edited</p>',
            'category': str(cat.id),
            'brand': str(brand.id),
            'price': 12.99,
            'cost': 8.00,
            'old_price': 18.00,
            'status': 'false'
        }, follow_redirects=True)
        assert res.status_code == 200, "Product Edit failed"
        
        prod = Product.query.get(prod.id)
        assert prod.name == 'Test Product Mobile Edited', "Product edit not in database"
        print(" -> Product Update: PASS")

        # Fast Image Upload
        res = client.post(f'/admin/mobile/product/fast-image-upload/{prod.id}', data={
            'image': (io.BytesIO(b"dummy image content"), 'fast_test.jpg')
        }, follow_redirects=True)
        assert res.status_code == 200, "Fast image upload failed"
        import json
        resp_data = json.loads(res.data)
        assert resp_data['status'] == 'success', "Fast image upload response status not success"
        assert resp_data['filename'] is not None, "Fast image upload did not return new filename"
        
        prod = Product.query.get(prod.id)
        assert prod.image == resp_data['filename'], "Product image in database did not update"
        print(" -> Product Fast Image Upload: PASS")

        # Test Telegram Post - without config (should return 400)
        res = client.post(f'/admin/mobile/product/telegram/{prod.id}', json={
            'caption': 'Test Telegram Post'
        })
        assert res.status_code == 400, "Should fail without config"
        resp_data = json.loads(res.data)
        assert resp_data['status'] == 'error'
        assert "configure Telegram" in resp_data['message']
        print(" -> Telegram Post Config Validation: PASS")

        # Test Telegram Post - with dummy config (should fail on invalid token)
        from models.Setting import Setting
        Setting.set_val("telegram_bot_token", "123456:DummyToken")
        Setting.set_val("telegram_chat_id", "@dummy_channel")
        
        res = client.post(f'/admin/mobile/product/telegram/{prod.id}', json={
            'caption': 'Test Telegram Post'
        })
        assert res.status_code == 400, "Should return 400 for invalid token"
        resp_data = json.loads(res.data)
        assert resp_data['status'] == 'error'
        assert "Telegram API" in resp_data['message']
        print(" -> Telegram API Communication: PASS")

        # Cleanup dummy settings
        Setting.query.filter(Setting.key.in_(['telegram_bot_token', 'telegram_chat_id'])).delete(synchronize_session=False)
        db.session.commit()

        # ------------------------------------------------------------
        # Test 4: User CRUD
        # ------------------------------------------------------------
        print("\n[4/6] Testing User CRUD...")
        # Create
        res = client.post('/admin/mobile/user/add', data={
            'username': 'testusermobile',
            'phone': '012345678',
            'password': 'testpassword123'
        }, follow_redirects=True)
        assert res.status_code == 200, "User Add failed"
        
        usr = User.query.filter_by(username='testusermobile').first()
        assert usr is not None, "User not found in Database"
        print(" -> User Creation: PASS")

        # Read
        res = client.get('/admin/mobile/user')
        assert res.status_code == 200, "User list page failed"
        print(" -> User Listing & Retrieval: PASS")

        # Update
        res = client.post(f'/admin/mobile/user/edit/{usr.id}', data={
            'username': 'testusermobile_edited',
            'phone': '098765432',
            'password': ''
        }, follow_redirects=True)
        assert res.status_code == 200, "User Edit failed"
        
        usr = User.query.get(usr.id)
        assert usr.username == 'testusermobile_edited', "User edit not in database"
        print(" -> User Update: PASS")

        # ------------------------------------------------------------
        # Test 5: Promotion CRUD
        # ------------------------------------------------------------
        print("\n[5/6] Testing Banner/Promotion CRUD...")
        # Create
        res = client.post('/admin/mobile/promotion/add', data={
            'image': (io.BytesIO(b"dummy image content"), 'test.jpg'),
            'title': 'Test Promo Mobile',
            'subtitle': 'Promo subtitle',
            'link': 'http://test.com',
            'button_text': 'Click here',
            'is_active': 'true'
        }, follow_redirects=True)
        assert res.status_code == 200, "Promotion Add failed"
        
        promo = Promotion.query.filter_by(title='Test Promo Mobile').first()
        if promo is None:
            print("--- Banner creation failed! Dumping page response for diagnostic ---")
            print(res.data.decode('utf-8', errors='ignore'))
            print("-------------------------------------------------------------------")
        assert promo is not None, "Promo not found in Database"
        print(" -> Banner Creation: PASS")

        # Read
        res = client.get('/admin/mobile/promotion')
        assert res.status_code == 200, "Promotion list page failed"
        print(" -> Banner Listing & Retrieval: PASS")

        # Update
        res = client.post(f'/admin/mobile/promotion/edit/{promo.id}', data={
            'title': 'Test Promo Mobile Edited',
            'subtitle': 'Promo subtitle edited',
            'link': 'http://test-edited.com',
            'button_text': 'Click here',
            'is_active': 'false'
        }, follow_redirects=True)
        assert res.status_code == 200, "Promotion Edit failed"
        
        promo = Promotion.query.get(promo.id)
        assert promo.title == 'Test Promo Mobile Edited', "Promo edit not in database"
        print(" -> Banner Update: PASS")

        # ------------------------------------------------------------
        # Test 6: Voucher CRUD
        # ------------------------------------------------------------
        print("\n[6/6] Testing Voucher CRUD...")
        # Create
        res = client.post('/admin/mobile/voucher/add', data={
            'code': 'TESTVOUCH123',
            'min_spend': 50.00,
            'usage_limit': 100,
            'usage_count': 0,
            'status': 'true'
        }, follow_redirects=True)
        assert res.status_code == 200, "Voucher Add failed"
        
        vouch = Voucher.query.filter_by(code='TESTVOUCH123').first()
        assert vouch is not None, "Voucher not found in Database"
        print(" -> Voucher Creation: PASS")

        # Read
        res = client.get('/admin/mobile/voucher')
        assert res.status_code == 200, "Voucher list page failed"
        print(" -> Voucher Listing & Retrieval: PASS")

        # Update
        res = client.post(f'/admin/mobile/voucher/edit/{vouch.id}', data={
            'code': 'TESTVOUCH123_EDITED',
            'min_spend': 40.00,
            'usage_limit': 50,
            'usage_count': 5,
            'status': 'false'
        }, follow_redirects=True)
        assert res.status_code == 200, "Voucher Edit failed"
        
        vouch = Voucher.query.get(vouch.id)
        assert vouch.code == 'TESTVOUCH123_EDITED', "Voucher edit not in database"
        print(" -> Voucher Update: PASS")

        # ------------------------------------------------------------
        # Clean up deletions
        # ------------------------------------------------------------
        print("\nCleaning up test entities...")
        # Delete
        client.post(f'/admin/mobile/product/delete/{prod.id}', follow_redirects=True)
        client.post(f'/admin/mobile/category/delete/{cat.id}', follow_redirects=True)
        client.post(f'/admin/mobile/brand/delete/{brand.id}', follow_redirects=True)
        client.post(f'/admin/mobile/user/delete/{usr.id}', follow_redirects=True)
        client.post(f'/admin/mobile/promotion/delete/{promo.id}', follow_redirects=True)
        client.post(f'/admin/mobile/voucher/delete/{vouch.id}', follow_redirects=True)
        
        # Verify deletions
        assert Product.query.get(prod.id) is None, "Product delete failed"
        assert Category.query.get(cat.id) is None, "Category delete failed"
        assert Brand.query.get(brand.id) is None, "Brand delete failed"
        assert User.query.get(usr.id) is None, "User delete failed"
        assert Promotion.query.get(promo.id) is None, "Promotion delete failed"
        assert Voucher.query.get(vouch.id) is None, "Voucher delete failed"
        print(" -> Deletion & Cleanup: PASS")

        print("\n" + "=" * 60)
        print("SUCCESS: ALL 6 MOBILE PORTAL CRUD FLOWS COMPLETED SUCCESSFULLY!")
        print("=" * 60)

if __name__ == '__main__':
    test_crud()
