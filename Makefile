.PHONY: build-LambdaLayer
build-LambdaLayer:
	docker run --rm \
		-v $(PWD):/var/task \
		-v $(ARTIFACTS_DIR):/var/artifacts \
		--platform linux/x86_64 \
		--entrypoint /bin/sh \
		public.ecr.aws/lambda/python:3.12-x86_64 \
		-c "\
			/var/lang/bin/pip install uv && \
			/var/lang/bin/uv build && \
			/var/lang/bin/pip install /var/task/dist/*.whl -t /var/artifacts/python"
