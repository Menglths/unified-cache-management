import json
import os
import random
from pathlib import Path
from typing import Any, Dict, List

import yaml
from common.llmperf.utils.token_benchmark import run_token_benchmark
from common.llmperf.utils.utils import reset_prefill_cache
from sympy import false


def run_test_cases(test_cases, timestamp_dir, model, server_url, tokenizer_path, repeated_number: int):
    """
    Execute all test cases and return the list of failed case indices and hit_rate mapping for each case.
    Parameters:
        test_cases    — List of test cases read from the configuration file
        timestamp_dir — Directory Path to save results
        model         — Model name
        server_url    — Base URL of the service
        tokenizer_path— Path to the tokenizer
    Returns:
        failed_cases       — List of failed case indices
    """
    print(f"[INFO] Total {len(test_cases)} test cases to be executed")
    all_summaries = []
    failed_case = []

    # Clear proxy environment variables
    env = os.environ.copy()
    env.pop("http_proxy", None)
    env.pop("https_proxy", None)

    for i, case in enumerate(test_cases):
        print(f"\n>>> Executing test case {i + 1} <<<")
        reset_prefill_cache(env, server_url)
        # Use a fixed random_seed for each test to control PC hit_rate
        random_seed = repeated_number if repeated_number != 0 else random.randint(1, 100000)
        summary = {}

        # Read parameters from configuration file
        mean_input = case.get("mean_input_tokens", 5000)
        stddev_input = case.get("stddev_input_tokens", 0)
        mean_output = case.get("mean_output_tokens", 1000)
        stddev_output = case.get("stddev_output_tokens", 0)
        max_completed = case.get("max_num_completed_requests", 1)
        concurrent = case.get("concurrent_requests", 1)
        llm_api = case.get("llm_api", "openai")
        additional_sampling_params = case.get("additional_sampling_params", "{}")
        timeout = case.get("timeout", 60000)
        hit_rate = case.get("hit_rate", 0)

        try:
            # Determine if two runs are needed (PC hit_rate test)
            if hit_rate == 0:
                summary = run_token_benchmark(
                    llm_api=llm_api,
                    model=model,
                    test_timeout_s=timeout,
                    max_num_completed_requests=max_completed,
                    concurrent_requests=concurrent,
                    mean_input_tokens=mean_input,
                    stddev_input_tokens=stddev_input,
                    mean_output_tokens=mean_output,
                    stddev_output_tokens=stddev_output,
                    additional_sampling_params=additional_sampling_params,
                    results_dir=str(timestamp_dir),
                    random_seed=random_seed,
                    openai_api_base=server_url + "/v1",
                    tokenizer_path=tokenizer_path,
                    user_metadata={"case_idx": i, "phase": "normal"},
                )
            else:
                print(
                    f"[INFO] hit_rate > 0 detected, entering prefill mode, PC hit rate: {hit_rate} %"
                )
                # hit_rate > 0: first prefill mode
                prefill_mean_input = int(mean_input * hit_rate / 100)
                print(
                    f"[INFO] Prefill execution: mean_input_tokens={prefill_mean_input}"
                )
                run_token_benchmark(
                    llm_api=llm_api,
                    model=model,
                    test_timeout_s=timeout,
                    max_num_completed_requests=max_completed,
                    concurrent_requests=concurrent,
                    mean_input_tokens=prefill_mean_input,
                    stddev_input_tokens=stddev_input,
                    mean_output_tokens=2,
                    stddev_output_tokens=stddev_output,
                    additional_sampling_params=additional_sampling_params,
                    results_dir=str(timestamp_dir),
                    random_seed=random_seed,
                    openai_api_base=server_url + "/v1",
                    tokenizer_path=tokenizer_path,
                    user_metadata={"case_idx": i, "phase": "prefill"},
                )
                reset_prefill_cache(env, server_url)
                # Then run normal mode
                print("[INFO] Prefill completed, switching to normal mode execution")
                summary = run_token_benchmark(
                    llm_api=llm_api,
                    model=model,
                    test_timeout_s=timeout,
                    max_num_completed_requests=max_completed,
                    concurrent_requests=concurrent,
                    mean_input_tokens=mean_input,
                    stddev_input_tokens=stddev_input,
                    mean_output_tokens=mean_output,
                    stddev_output_tokens=stddev_output,
                    additional_sampling_params=additional_sampling_params,
                    results_dir=str(timestamp_dir),
                    random_seed=random_seed,
                    openai_api_base=server_url + "/v1",
                    tokenizer_path=tokenizer_path,
                    user_metadata={"case_idx": i, "phase": "normal"},
                )
            all_summaries.append(summary)
        except Exception as e:
            failed_case.append(i)

    return all_summaries, failed_case


"""
KV Pool 支持并发读写测试    可以并发执行20个推理任务，然后再次执行并发10个任务，这10个任务是前面20个推理任务中的第一个任务
"""
def support_current_test(test_cases, timestamp_dir, model, server_url, tokenizer_path, repeated_number):
    """
    Execute all test cases and return the list of failed case indices and hit_rate mapping for each case.
    Parameters:
        test_cases    — List of test cases read from the configuration file
        timestamp_dir — Directory Path to save results
        model         — Model name
        server_url    — Base URL of the service
        tokenizer_path— Path to the tokenizer
    Returns:
        failed_cases       — List of failed case indices
    """
    print(f"[INFO] Total {len(test_cases)} test cases to be executed")
    all_summaries = []
    failed_case = []

    # Clear proxy environment variables
    env = os.environ.copy()
    env.pop("http_proxy", None)
    env.pop("https_proxy", None)

    for i, case in enumerate(test_cases):
        print(f"\n>>> Executing test case {i + 1} <<<")
        reset_prefill_cache(env, server_url)
        # Use a fixed random_seed for each test to control PC hit_rate
        random_seed = repeated_number if repeated_number != 0 else random.randint(1, 100000)
        summary = {}

        # Read parameters from configuration file
        mean_input = case.get("mean_input_tokens", 5000)
        stddev_input = case.get("stddev_input_tokens", 0)
        mean_output = case.get("mean_output_tokens", 1000)
        stddev_output = case.get("stddev_output_tokens", 0)
        max_completed = case.get("max_num_completed_requests", 1)
        concurrent = case.get("concurrent_requests", 1)
        llm_api = case.get("llm_api", "openai")
        additional_sampling_params = case.get("additional_sampling_params", "{}")
        execute_phase = case.get("execute_phase", "normal")
        timeout = case.get("timeout", 60000)

        try:
            print(f"[INFO] support_current is true, entering concurrent mode")
            print(
                f"[INFO] Execution: mean_input_tokens={mean_input}"
            )
            summary = run_token_benchmark(
                llm_api=llm_api,
                model=model,
                test_timeout_s=timeout,
                max_num_completed_requests=max_completed,
                concurrent_requests=concurrent,
                mean_input_tokens=mean_input,
                stddev_input_tokens=stddev_input,
                mean_output_tokens=mean_output,
                stddev_output_tokens=stddev_output,
                additional_sampling_params=additional_sampling_params,
                results_dir=str(timestamp_dir),
                random_seed=random_seed,
                openai_api_base=server_url + "/v1",
                tokenizer_path=tokenizer_path,
                user_metadata={"case_idx": i, "phase": execute_phase},
            )
            all_summaries.append(summary)
        except Exception as e:
            print(e)
            failed_case.append(i)

    return all_summaries, failed_case


def inference_results():
    config_file = Path(__file__).parent.parent.parent / "config.yaml"
    all_smmaries = {}
    print("[INFO] Initialization complete, starting main process")
    print(f"[INFO] Reading configuration file: {config_file}")
    with open(config_file, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        model = config.get("llm_connection", {}).get("model", "")
        server_url = config.get("llm_connection", {}).get("server_url", "")
        tokenizer_path = config.get("llm_connection", {}).get("tokenizer_path", "")
        repeated_number = config.get("llm_connection", {}).get("repeated_number", "")
        support_concurrent = config.get("llm_connection", {}).get("support_concurrent", "")
        test_cases = config.get("llmperf_test_cases", [])
        timestamp_dir = Path("results")
        timestamp_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Created results directory: {timestamp_dir}")

        if support_concurrent is False:
            # 测试类型一，多次执行保证推理结果一致
            all_summaries, failed_cases = run_test_cases(
                test_cases, timestamp_dir, model, server_url, tokenizer_path, repeated_number
            )
        else:
            # 测试类型二，支持并发读写
            all_summaries, failed_cases = support_current_test(
                test_cases, timestamp_dir, model, server_url, tokenizer_path, repeated_number
            )

        total = len(test_cases)
        print(
            f"\n[INFO] All tests completed! Success: {total - len(failed_cases)}/{total}"
        )
        if failed_cases:
            print(f"[WARN] Failed case indices: {failed_cases}")
    return all_summaries
