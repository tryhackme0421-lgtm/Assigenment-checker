import requests
import sys
import json
import io
from datetime import datetime

class SmartAssignmentCheckerTester:
    def __init__(self, base_url="https://markmate-6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.submission_id = None

    def run_test(self, name, method, endpoint, expected_status, data=None, files=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {}
        if not files:
            headers['Content-Type'] = 'application/json'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    response = requests.post(url, files=files, data=data)
                else:
                    response = requests.post(url, json=data, headers=headers)

            print(f"   Status Code: {response.status_code}")
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API Endpoint", "GET", "", 200)

    def test_login_success(self):
        """Test successful login"""
        return self.run_test(
            "Login Success",
            "POST",
            "login",
            200,
            data={"username": "admin", "password": "admin123"}
        )

    def test_login_failure(self):
        """Test failed login"""
        return self.run_test(
            "Login Failure",
            "POST",
            "login",
            401,
            data={"username": "wrong", "password": "wrong"}
        )

    def test_stats_endpoint(self):
        """Test dashboard statistics"""
        return self.run_test("Dashboard Stats", "GET", "stats", 200)

    def test_submissions_endpoint(self):
        """Test get submissions"""
        return self.run_test("Get Submissions", "GET", "submissions", 200)

    def test_file_upload(self):
        """Test file upload with a sample text file"""
        # Create a sample assignment text file
        sample_content = """
        Name: John Doe
        Roll Number: CS2021001
        Assignment: Data Structures and Algorithms
        
        This is a sample assignment submission about binary search trees.
        A binary search tree is a hierarchical data structure where each node
        has at most two children, and the left child is always smaller than
        the parent, while the right child is always greater.
        
        Implementation:
        class TreeNode:
            def __init__(self, val=0, left=None, right=None):
                self.val = val
                self.left = left
                self.right = right
        
        The time complexity for search operations is O(log n) in the average case.
        """
        
        # Create file-like object
        file_data = io.BytesIO(sample_content.encode('utf-8'))
        files = {'file': ('sample_assignment.txt', file_data, 'text/plain')}
        
        success, response = self.run_test(
            "File Upload",
            "POST", 
            "upload",
            200,
            files=files
        )
        
        if success and 'id' in response:
            self.submission_id = response['id']
            print(f"   Submission ID: {self.submission_id}")
        
        return success, response

    def test_get_specific_submission(self):
        """Test getting a specific submission"""
        if not self.submission_id:
            print("❌ Skipping - No submission ID available")
            return False, {}
        
        return self.run_test(
            "Get Specific Submission",
            "GET",
            f"submission/{self.submission_id}",
            200
        )

    def test_evaluate_assignment(self):
        """Test AI evaluation of assignment"""
        if not self.submission_id:
            print("❌ Skipping - No submission ID available")
            return False, {}
        
        return self.run_test(
            "Evaluate Assignment",
            "POST",
            "evaluate",
            200,
            data={
                "submission_id": self.submission_id,
                "max_marks": 20,
                "evaluator_name": "Test Admin"
            }
        )

    def test_excel_export(self):
        """Test Excel export functionality"""
        url = f"{self.api_url}/export/excel"
        print(f"\n🔍 Testing Excel Export...")
        print(f"   URL: {url}")
        
        self.tests_run += 1
        
        try:
            response = requests.get(url)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                # Check if it's actually an Excel file
                content_type = response.headers.get('content-type', '')
                if 'spreadsheet' in content_type or 'excel' in content_type:
                    self.tests_passed += 1
                    print(f"✅ Passed - Excel file downloaded successfully")
                    print(f"   Content-Type: {content_type}")
                    print(f"   Content-Length: {len(response.content)} bytes")
                    return True, {}
                else:
                    print(f"❌ Failed - Not an Excel file. Content-Type: {content_type}")
                    return False, {}
            else:
                print(f"❌ Failed - Status: {response.status_code}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_invalid_file_upload(self):
        """Test upload with invalid file type"""
        # Create a fake image file
        file_data = io.BytesIO(b"fake image content")
        files = {'file': ('test.jpg', file_data, 'image/jpeg')}
        
        return self.run_test(
            "Invalid File Upload",
            "POST",
            "upload", 
            400,
            files=files
        )

def main():
    print("🚀 Starting Smart Assignment Checker Backend Tests")
    print("=" * 60)
    
    tester = SmartAssignmentCheckerTester()
    
    # Test sequence
    test_results = []
    
    # Basic API tests
    test_results.append(tester.test_root_endpoint())
    test_results.append(tester.test_login_success())
    test_results.append(tester.test_login_failure())
    test_results.append(tester.test_stats_endpoint())
    test_results.append(tester.test_submissions_endpoint())
    
    # File upload and processing tests
    test_results.append(tester.test_file_upload())
    test_results.append(tester.test_get_specific_submission())
    
    # AI evaluation test (this might take longer)
    print("\n⏳ Testing AI evaluation (this may take 10-30 seconds)...")
    test_results.append(tester.test_evaluate_assignment())
    
    # Export functionality
    test_results.append(tester.test_excel_export())
    
    # Error handling tests
    test_results.append(tester.test_invalid_file_upload())
    
    # Print final results
    print("\n" + "=" * 60)
    print("📊 BACKEND TEST RESULTS")
    print("=" * 60)
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Tests Failed: {tester.tests_run - tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("\n🎉 All backend tests passed!")
        return 0
    else:
        print(f"\n⚠️  {tester.tests_run - tester.tests_passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())