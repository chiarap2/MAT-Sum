# MAT-Sum

`MAT-Sum` is a method that allows us to obtain summarized semantic trajectories, starting from both raw and semantically enriched trajectories. It enriches with semantic aspects the underlying geographical context and leverages it to summarize trajectories.

The input could be both a check-in or a gps dataset, in `csv` or `parquet` format. The output will be a set of semantically enriched locations traversed by trajectories. 

To run `MAT-Sum`, please run the following code after installing requirements in `requirements.txt` file and moving in the `mat_sum` folder:
```
python main.py
```

You can config it w.r.t. your own datasets by modifying the `config.json` file in the `configs` folder. In the same folder, you can config your experimental setup. In `config` and `config-gps` folders there are some examples of experimental configurations.

In the `data` folder, you find some sample of the dataset used in our experiments: Foursquare NYC check-ins and Geolife GPS trajectories.

In the `evaluation` folder, you find the metrics and the results we obtain with all parameters configurations and w.r.t. two baselines: RLE and Seqscan-D.

In the `output` and `output-gps` folders, you find the output of each step of this method in `.parquet` extension.