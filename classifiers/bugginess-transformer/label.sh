python classifiers/bugginess-transformer/run.py --model_name_or_path models \
              --do_predict \
              --evaluation_strategy steps \
              --eval_steps 0 \
              --eval_test \
              --output_dir "$2" \
	          --per_device_eval_batch_size 14 \
              --data_file "$1"
