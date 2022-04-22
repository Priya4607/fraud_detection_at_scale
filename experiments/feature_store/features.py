from feast import Entity, Feature, FeatureView, FileSource, ValueType
from google.protobuf.duration_pb2 import Duration

aggregated_output = FileSource(
    path="./data/processed/aggregated_output.parquet", event_timestamp_column="ts"
)

cc_num = Entity(name="cc_num", value_type=ValueType.INT64, description="cc_num",)

cc_weekly = FeatureView(
    name="cc_weekly",
    entities=["cc_num"],
    ttl=Duration(seconds=86400 * 1),
    features=[
        Feature(name="num_trans_last_1w", dtype=ValueType.DOUBLE),
        Feature(name="avg_amt_last_1w", dtype=ValueType.DOUBLE),
    ],
    online=True,
    batch_source=aggregated_output,
    tags={},
)

cc_latest = FeatureView(
    name="cc_latest",
    entities=["cc_num"],
    ttl=Duration(seconds=86400 * 1),
    features=[
        Feature(name="num_trans_last_10m", dtype=ValueType.DOUBLE),
        Feature(name="avg_amt_last_10m", dtype=ValueType.DOUBLE),
    ],
    online=True,
    batch_source=aggregated_output,
    tags={},
)
