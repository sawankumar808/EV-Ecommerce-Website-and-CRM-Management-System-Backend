from rest_framework import serializers
from .models import BatteryBatch, Battery, BatteryStatusHistory


class BatteryBatchSerializer(serializers.ModelSerializer):
    generated_count = serializers.SerializerMethodField()

    class Meta:
        model = BatteryBatch
        fields = "__all__"

    def get_generated_count(self, obj):
        return obj.batteries.count()


class BatteryStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BatteryStatusHistory
        fields = "__all__"


class BatterySerializer(serializers.ModelSerializer):
    batch_number = serializers.CharField(source="batch.batch_number", read_only=True)

    class Meta:
        model = Battery
        fields = "__all__"


class BatteryDetailSerializer(BatterySerializer):
    history = BatteryStatusHistorySerializer(many=True, read_only=True)

    class Meta(BatterySerializer.Meta):
        pass
