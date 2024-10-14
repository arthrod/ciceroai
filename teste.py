import json
import os
import tempfile

import torch
from accelerate import (
    Accelerator,
    PartialState,
    init_empty_weights,
    load_checkpoint_and_dispatch,
)
from accelerate.big_modeling import load_checkpoint_and_dispatch
from accelerate.utils import set_seed
from huggingface_hub import hf_hub_download
from torch.utils.data import DataLoader
from tqdm import tqdm
from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

from datasets import load_dataset

# Set the environment variable
os.environ["OMP_NUM_THREADS"] = "200"


def collate_fn(batch):
    conversations = [item["conversations"] for item in batch]
    prompts = [conv[0]["value"] for conv in conversations]
    responses = [conv[1]["value"] for conv in conversations]
    return {"prompts": prompts, "responses": responses}


def main():
    os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:512"
    os.environ["TMPDIR"] = "/mnt/large_storage/tmp"
    os.environ["HF_HOME"] = "/mnt/large_storage/.cache/huggingface"
    os.environ["TORCH_HOME"] = "/mnt/large_storage/.cache/torch"
    os.makedirs("/mnt/large_storage/tmp", exist_ok=True)  # Initialize
    tempfile.tempdir = "/mnt/large_storage/tmp"  # Accelerator
    accelerator = Accelerator(mixed_precision="bf16")
    state = PartialState()

    # Configuration
    generation_file = "/mnt/large_storage/boca.jsonl"
    reward_model_name = "nvidia/Llama-3.1-Nemotron-70B-Reward-HF"
    output_dir = "/mnt/large_storage/datasets/"
    os.makedirs(output_dir, exist_ok=True)
    cache_dir = "/mnt/large_storage/.cache/huggingface"
    # Get the cached weights location
    weights_location = hf_hub_download(
        reward_model_name, "model.safetensors.index.json", cache_dir=cache_dir
    )
    batch_size = 1  # Adjust based on GPU memory

    max_memory = {
        0: "65GB",  # 70GB for GPU 0
        1: "70GB",
        2: "70GB",
        3: "70GB",
        4: "70GB",
        5: "70GB",
        6: "70GB",
        7: "70GB",
    }

    set_seed(42)
    print("Starting script execution...")

    # Load model and tokenizer
    print("Loading model and tokenizer...")

    # Explicitly specify the model name and cache directory
    config = AutoConfig.from_pretrained(reward_model_name, cache_dir=cache_dir)
    with init_empty_weights():
        model = AutoModelForCausalLM.from_config(config)

    model = load_checkpoint_and_dispatch(
        model,
        weights_location,
        device_map="auto",
        max_memory=max_memory,
        offload_folder="/dev/shm/model_offload",  # Using /dev/shm for faster I/
        offload_state_dict=True,
        dtype=torch.bfloat16,
    )
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=reward_model_name, cache_dir=cache_dir
    )
    tokenizer.pad_token = tokenizer.eos_token

    print(f"Model loaded. Number of parameters: {model.num_parameters():,}")

    # Load dataset
    print(f"Loading dataset from {generation_file}...")

    # dataset = load_dataset("json", data_files=generation_file, split="train")
    dataset = load_dataset("json", data_files=generation_file, split="train[:100]")
    print(f"Dataset loaded. Number of samples: {len(dataset):,}")

    # Create DataLoader
    dataloader = DataLoader(
        dataset, batch_size=batch_size, collate_fn=collate_fn, shuffle=False
    )

    # Prepare model and dataloader
    model, dataloader = accelerator.prepare(model, dataloader)

    # Process data using pipeline parallel model
    output_data = []

    for batch in tqdm(dataloader, desc="Processing batches"):
        prompts = batch["prompts"]
        responses = batch["responses"]

        inputs = tokenizer(
            prompts, responses, return_tensors="pt", padding=True, truncation=True
        )
        inputs = {k: v.to(accelerator.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)

        # Process outputs
        next_token_logits = outputs[0][:, -1, :]
        rewards = next_token_logits[
            :, 0
        ].tolist()  # Assuming the reward is the first token logit

        for prompt, response, reward in zip(prompts, responses, rewards):
            output_data.append(
                {"prompt": prompt, "response": response, "reward_score": reward}
            )

        # Save after each batch
        if accelerator.is_main_process:
            save_outputs(output_data, output_dir, generation_file)
            print(f"Saved outputs. Total processed: {len(output_data):,}")

    # Final save and binarization
    if accelerator.is_main_process:
        save_outputs(output_data, output_dir, generation_file)
        binarize_outputs(output_data, output_dir, generation_file)
        print(
            f"Finished processing all batches. Total samples processed: {len(output_data):,}"
        )

    accelerator.wait_for_everyone()

    # Print statement
    print("stat34em")


def save_outputs(output_data, output_dir, generation_file):
    output_file = os.path.join(
        output_dir, os.path.basename(generation_file).replace(".jsonl", "_rm.jsonl")
    )
    with open(output_file, "w") as f:
        for item in output_data:
            json.dump(item, f)
            f.write("\n")
    print(
        f"Outputs saved to {output_file}. Number of items saved: {len(output_data):,}"
    )


def binarize_outputs(output_data, output_dir, generation_file):
    print(f"Binarizing outputs. Number of items to process: {len(output_data):,}")
    binarized_data = []
    for data in output_data:
        binarized_data.append(
            {
                "prompt": data["prompt"],
                "chosen": data["response"],
                "rejected": "",  # We don't have a rejected response in this case
                "chosen_score": data["reward_score"],
                "rejected_score": 0,  # We don't have a rejected score in this case
            }
        )

    output_file = os.path.join(
        output_dir, os.path.basename(generation_file).replace(".jsonl", "_bin.jsonl")
    )
    with open(output_file, "w") as f:
        for item in binarized_data:
            json.dump(item, f)
            f.write("\n")
    print(
        f"Binarized outputs saved to {output_file}. Number of items saved: {len(binarized_data):,}"
    )


if __name__ == "__main__":
    main()
