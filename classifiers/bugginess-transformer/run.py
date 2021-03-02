# coding=utf-8
# Copyright 2018 The Google AI Language Team Authors and The HuggingFace Inc. team.
# Copyright (c) 2018, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Finetuning the library models for sequence classification on GLUE (Bert, XLM, XLNet, RoBERTa, Albert, XLM-RoBERTa)."""


import dataclasses
import logging
import math
import os
import sys
import textwrap
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

os.environ["WANDB_DISABLED"] = "true"

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, TensorDataset
from transformers import (
    AutoConfig,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    EvalPrediction,
    HfArgumentParser,
    Trainer,
    TrainingArguments,
    set_seed,
)

logger = logging.getLogger(__name__)

LABEL_NAMES = [
    "BUGLESS",
    "BUG",
]

LABEL_MAP = {l: i for i, l in enumerate(LABEL_NAMES)}
print(LABEL_MAP)


@dataclass
class ModelArguments:
    """
    Arguments pertaining to which model/config/tokenizer we are going to fine-tune from.
    """

    data_file: str = field()
    model_name_or_path: str = field(
        metadata={
            "help": "Path to pretrained model or model identifier from huggingface.co/models"
        }
    )
    config_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained config name or path if not the same as model_name"
        },
    )
    tokenizer_name: Optional[str] = field(
        default=None,
        metadata={
            "help": "Pretrained tokenizer name or path if not the same as model_name"
        },
    )
    cache_dir: Optional[str] = field(
        default=None,
        metadata={
            "help": "Where do you want to store the pretrained models downloaded from s3"
        },
    )
    output_mode: Optional[str] = field(default="classification")
    eval_test: bool = field(default=False)


class SimpleDataset(Dataset):
    def __init__(self, input_ids, attention_masks, label_ids):
        self.len = input_ids.shape[0]
        self.input_ids = input_ids
        self.attention_masks = attention_masks
        self.label_ids = label_ids

    def __len__(self):
        return self.len

    def __getitem__(self, index):
        return {
            "label": self.label_ids[index],
            "input_ids": self.input_ids[index],
            "attention_mask": self.attention_masks[index],
        }


def main():
    # See all possible arguments in src/transformers/training_args.py
    # or by passing the --help flag to this script.
    # We now keep distinct sets of args, for a cleaner separation of concerns.

    parser = HfArgumentParser((ModelArguments, TrainingArguments))
    model_args, training_args = parser.parse_args_into_dataclasses()
    print(model_args)
    print(training_args)

    if (
        os.path.exists(training_args.output_dir)
        and os.listdir(training_args.output_dir)
        and training_args.do_train
        and not training_args.overwrite_output_dir
    ):
        raise ValueError(
            f"Output directory ({training_args.output_dir}) already exists and is not empty. Use --overwrite_output_dir to overcome."
        )

    # Setup logging
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO if training_args.local_rank in [-1, 0] else logging.WARN,
    )
    logger.warning(
        "Process rank: %s, device: %s, n_gpu: %s, distributed training: %s, 16-bits training: %s",
        training_args.local_rank,
        training_args.device,
        training_args.n_gpu,
        bool(training_args.local_rank != -1),
        training_args.fp16,
    )
    logger.info("Training/evaluation parameters %s", training_args)

    # Set seed
    set_seed(training_args.seed)

    num_labels = len(LABEL_NAMES)

    # Load pretrained model and tokenizer
    #
    # Distributed training:
    # The .from_pretrained methods guarantee that only one local process can concurrently
    # download model & vocab.

    config = AutoConfig.from_pretrained(
        model_args.config_name
        if model_args.config_name
        else model_args.model_name_or_path,
        num_labels=num_labels,
        cache_dir=model_args.cache_dir,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        model_args.tokenizer_name
        if model_args.tokenizer_name
        else model_args.model_name_or_path,
        cache_dir=model_args.cache_dir,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        model_args.model_name_or_path,
        from_tf=bool(".ckpt" in model_args.model_name_or_path),
        config=config,
        cache_dir=model_args.cache_dir,
    )

    # config = RobertaConfig.from_pretrained(
    #     model_args.config_name if model_args.config_name else model_args.model_name_or_path,
    #     num_labels=num_labels,
    #     # hidden_dropout_prob=0.00,
    #     cache_dir=model_args.cache_dir,
    # )
    # tokenizer = RobertaTokenizerFast.from_pretrained(
    #     model_args.tokenizer_name if model_args.tokenizer_name else model_args.model_name_or_path,
    #     cache_dir=model_args.cache_dir,
    #     do_lower_case=False
    # )
    # model = HeadlessRobertaForSequenceClassification.from_pretrained(
    #     model_args.model_name_or_path,
    #     from_tf=bool(".ckpt" in model_args.model_name_or_path),
    #     config=config,
    #     cache_dir=model_args.cache_dir,
    # )

    def df_to_dataset(df):
        print("Loading dataset...")
        df = df[df.bug != -1]
        df = df[~df.message.isnull()]

        text_values = df.message.values
        label_ids = df.bug.values

        text_values_list = text_values.tolist()
        for elm in text_values_list:
            if not isinstance(elm, str):
                print(elm)

        encoding = tokenizer(
            text_values_list,
            add_special_tokens=True,
            return_attention_mask=True,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors="pt",
        )

        input_ids = encoding["input_ids"]
        label_ids_dtype = torch.float32 if num_labels == 1 else torch.int64
        label_ids_t = torch.tensor(label_ids, dtype=label_ids_dtype)

        print(tokenizer.decode(input_ids[0, :].tolist()))

        print("DF shape: ", df.shape)
        print(input_ids.shape)
        print(label_ids_t.shape)

        dataset = SimpleDataset(input_ids, encoding["attention_mask"], label_ids_t)

        print("Done")
        return dataset

    if model_args.eval_test:
        print("**** TEST EVAL *****")
        test_df = pd.read_csv(model_args.data_file)
        eval_dataset = df_to_dataset(test_df)
        train_dataset = None
    else:
        print("**** TRAINING ******")
        train_valid_df = pd.read_csv(model_args.data_file)
        train_df, valid_df = train_test_split(
            train_valid_df, test_size=0.1, shuffle=False
        )
        train_dataset = df_to_dataset(train_df)
        eval_dataset = df_to_dataset(valid_df)

    output_mode = model_args.output_mode

    def compute_metrics_fn(p: EvalPrediction):
        if output_mode == "classification":
            preds = np.argmax(p.predictions, axis=1)
        else:
            raise ValueError()
            # elif output_mode == "regression":
        #    raise ValueError()
        #    preds = np.squeeze(p.predictions)
        print(preds)
        print(p.label_ids)

        print(
            classification_report(
                p.label_ids, preds, target_names=LABEL_NAMES, digits=3
            )
        )

        acc = accuracy_score(p.label_ids, preds)
        f1 = f1_score(p.label_ids, preds, average="macro")
        return {
            "acc": acc,
            "f1": f1,
        }

    # Initialize our Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        compute_metrics=compute_metrics_fn,
    )

    # Training
    if training_args.do_train:
        trainer.train(
            model_path=model_args.model_name_or_path
            if os.path.isdir(model_args.model_name_or_path)
            else None
        )
        trainer.save_model()
        # For convenience, we also re-save the tokenizer to the same directory,
        # so that you can share your model easily on huggingface.co/models =)
        if trainer.is_world_master():
            tokenizer.save_pretrained(training_args.output_dir)

    # Evaluation
    eval_results = {}
    if training_args.do_eval:
        logger.info("*** Evaluate ***")

        # Loop to handle MNLI double evaluation (matched, mis-matched)
        eval_datasets = [eval_dataset]

        for eval_dataset in eval_datasets:
            trainer.compute_metrics = compute_metrics_fn
            eval_result = trainer.evaluate(eval_dataset=eval_dataset)

            output_eval_file = os.path.join(
                training_args.output_dir, f"eval_results.txt"
            )
            if trainer.is_world_master():
                with open(output_eval_file, "w") as writer:
                    logger.info("***** Eval results *****")
                    for key, value in eval_result.items():
                        logger.info("  %s = %s", key, value)
                        writer.write("%s = %s\n" % (key, value))

            eval_results.update(eval_result)

    if training_args.do_predict:
        logging.info("*** Test ***")
        test_datasets = [test_dataset]

        for test_dataset in test_datasets:
            trainer.compute_metrics = compute_metrics_fn
            predictions = trainer.predict(test_dataset=test_dataset).predictions

            # if output_mode == "classification":
            #     predictions = np.argmax(predictions, axis=1)

            # output_test_file = os.path.join(
            #     training_args.output_dir, f"test_results.txt"
            # )
            # if trainer.is_world_master():
            #     with open(output_test_file, "w") as writer:
            #         logger.info("***** Test results *****")
            #         writer.write("index\tprediction\n")
            #         for index, item in enumerate(predictions):
            #             if output_mode == "regression":
            #                 writer.write("%d\t%3.3f\n" % (index, item))
            #             else:
            #                 item = test_dataset.get_labels()[item]
            #                 writer.write("%d\t%s\n" % (index, item))
    return eval_results


def _mp_fn(index):
    # For xla_spawn (TPUs)
    main()


if __name__ == "__main__":
    # import sys
    # sys.argv.extend(['--model_name_or_path', "giganticode/StackOBERTflow-comments-small-v1"])
    # sys.argv.extend(['--output_dir', 'bohr_model'])
    # sys.argv.extend(['--do_train'])
    # sys.argv.extend(['--do_eval'])
    # sys.argv.extend(['--per_device_train_batch_size', '14'])
    # sys.argv.extend(['--overwrite_output_dir'])
    # sys.argv.extend(['--save_steps', '4000'])
    # sys.argv.extend(['--num_train_epochs', '3'])
    # sys.argv.extend(['--logging_steps', '4000'])
    # sys.argv.extend(['--eval_steps', '4000'])
    # sys.argv.extend(['--evaluation_strategy', 'steps'])
    # sys.argv.extend(['--data_file', '/Users/hlib/dev/bohr/labeled-data/bugginess.csv'])
    main()
