import urllib.request
import json
import time

url = "http://localhost:11434/api/generate"
payload = {
    "model": "gemma3:latest",
    "prompt": "Explain machine learning to a college student in approximately 500 words.",
    "stream": False,
    "options": {
        "num_predict": 1000
    },
    "keep_alive": "30m"
}

def run_single_benchmark(run_number: int):
    print(f"\n--- Starting Benchmark Run #{run_number} (keep_alive: 30m) ---")
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

    start_time = time.perf_counter()
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    end_time = time.perf_counter()

    total_dur = res.get("total_duration", 0) / 1e9
    load_dur = res.get("load_duration", 0) / 1e9
    prompt_eval_cnt = res.get("prompt_eval_count", 0)
    prompt_eval_dur = res.get("prompt_eval_duration", 0) / 1e9
    eval_cnt = res.get("eval_count", 0)
    eval_dur = res.get("eval_duration", 0) / 1e9

    tps = eval_cnt / eval_dur if eval_dur > 0 else 0

    print("=======================================================")
    print(f" Run #{run_number} Wall Clock Time: {end_time - start_time:.2f} seconds")
    print(f" total_duration:       {total_dur:.2f} seconds")
    print(f" load_duration:        {load_dur:.2f} seconds")
    print(f" prompt_eval_count:    {prompt_eval_cnt} tokens")
    print(f" prompt_eval_duration: {prompt_eval_dur:.2f} seconds")
    print(f" eval_count:           {eval_cnt} tokens")
    print(f" eval_duration:        {eval_dur:.2f} seconds")
    print("=======================================================")
    print(f" GENERATION SPEED:     {tps:.2f} tokens/second")
    print("=======================================================")
    return {
        "wall_time": end_time - start_time,
        "load_duration": load_dur,
        "eval_count": eval_cnt,
        "eval_duration": eval_dur,
        "tps": tps
    }

if __name__ == "__main__":
    print("Starting Ollama Benchmark Dual Run Test...")
    res1 = run_single_benchmark(1)
    res2 = run_single_benchmark(2)

    print("\n=======================================================")
    print("           DUAL BENCHMARK COMPARISON SUMMARY           ")
    print("=======================================================")
    print(f" Run 1 Load Duration: {res1['load_duration']:.2f}s  | Total Wall Time: {res1['wall_time']:.2f}s | Speed: {res1['tps']:.2f} t/s")
    print(f" Run 2 Load Duration: {res2['load_duration']:.2f}s  | Total Wall Time: {res2['wall_time']:.2f}s | Speed: {res2['tps']:.2f} t/s")
    diff_load = res1['load_duration'] - res2['load_duration']
    print(f" VRAM Warm-up Load Savings: {diff_load:.2f} seconds saved on Run #2!")
    print("=======================================================")
