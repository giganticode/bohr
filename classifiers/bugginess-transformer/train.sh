python /Users/hlib/dev/bohr/classifiers/bugginess-transformer/run.py --model_name_or_path "giganticode/StackOBERTflow-comments-small-v1" \
              --output_dir bohr_model \
              --do_train \
              --do_eval \
              --per_device_train_batch_size 14 \
              --overwrite_output_dir \
              --save_steps 4000 \
              --num_train_epochs 3 \
              --logging_steps 4000 \
              --eval_steps 4000 \
              --evaluation_strategy steps \
              --data_file /Users/hlib/dev/bohr/labeled-data/bugginess.csv \
#               --fp16