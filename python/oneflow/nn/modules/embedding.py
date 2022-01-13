"""
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import warnings
from typing import Optional

import oneflow as flow
import oneflow._oneflow_internal
from oneflow.framework.tensor import register_tensor_op
from oneflow.nn.module import Module
from oneflow.nn.modules.utils import _check_inplace_valid
import json
import os


fixed_table_block_size = int(os.environ.get("FIXED_TABLE_BLOCK_SIZE", 512))
optimizer = str(os.environ.get("OPTIMIZER", "sgd"))


class OneEmbeddingLookup(Module):
    def __init__(self, options):
        super().__init__()
        self.dtype = options["dtype"]
        embedding_options = {
            "embedding_name": "EmbeddingTest",
            "embedding_size": int(os.environ.get("EMBEDDING_SIZE", 128)),
            "l1_cache": {"policy": "lru", "cache_memory_budget_mb": 8192,},
            "l2_cache": {"policy": "none",},
            "fixed_table": {
                "path": os.environ.get("BLOCK_BASED_PATH"),
                "block_size": fixed_table_block_size,
                "chunk_size": 4 * 1024 * 1024,
            },
            "initializer": {"type": "uniform", "mean": 0, "std": 1,},
            "optimizer": {
                "type": optimizer,
                "beta": 0.9,
                "beta1": 0.9,
                "beta2": 0.999,
                "epsilon": 1e-8,
                "do_bias_correction": True,
            },
            "learning_rate_schedule": {
                "learning_rate": 24,
                "learning_rate_decay": {
                    "type": "polynomial",
                    "decay_batches": 27772,
                    "end_learning_rate": 0.0,
                    "power": 2.0,
                    "cycle": False,
                },
                "warmup": {
                    "type": "linear",
                    "warmup_batches": 2750,
                    "start_multiplier": 0.0,
                },
            },
        }
        self.embedding_options = json.dumps(embedding_options)

    def forward(self, ids):
        return flow._C.embedding_lookup_placeholder(
            ids, self.dtype, self.embedding_options,
        )