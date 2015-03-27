.PHONY: all sl_builder

sl_builder:
	docker build -t onedata/sl_builder:v2 -f sl_builder .


