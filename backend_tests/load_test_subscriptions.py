import time
import requests
import threading
import concurrent.futures

# API Configuration
BASE_URL = "http://localhost:8000"
USER_ID = "load_test_user"
DEVICE_ID = "load_test_device"

def test_sync():
    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/subscription/sync",
            json={"userId": USER_ID, "deviceId": DEVICE_ID}
        )
        duration = time.time() - start
        return response.status_code == 200, duration
    except Exception as e:
        return False, 0

def run_load_test(num_requests=100, concurrent_users=10):
    print(f"🚀 Starting Load Test: {num_requests} requests, {concurrent_users} concurrent users")
    
    start_all = time.time()
    results = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(test_sync) for _ in range(num_requests)]
        for future in concurrent.futures.as_completed(futures):
            results.append(future.result())
    
    total_duration = time.time() - start_all
    successes = sum(1 for r in results if r[0])
    avg_duration = sum(r[1] for r in results) / len(results)
    
    print(f"\n📊 Results:")
    print(f"Total Requests: {len(results)}")
    print(f"Success Rate: {successes/len(results)*100:.1f}%")
    print(f"Total Time: {total_duration:.2f}s")
    print(f"Avg Request Time: {avg_duration*1000:.2f}ms")
    print(f"Requests Per Second: {len(results)/total_duration:.2f}")

if __name__ == "__main__":
    run_load_test()
