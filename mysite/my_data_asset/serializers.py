from rest_framework import serializers
from .models import (
    Asset,
    AssetType,
    AssetDomain,
    AssetDetails,
    # AssetColumn,
    # AssetCategory,
    # AssetCategoryRelation,
)


class AssetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetType
        fields = '__all__'


class AssetDomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDomain
        fields = '__all__'


class AssetDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssetDetails
        fields = '__all__'

# class AssetColumnSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AssetColumn
#         fields = '__all__'


# class AssetCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AssetCategory
#         fields = '__all__'


# class AssetCategoryRelationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = AssetCategoryRelation
#         fields = '__all__'

#
# class AssetSerializer(serializers.ModelSerializer):
#     type = AssetTypeSerializer(read_only=True)
#     domain = AssetDomainSerializer(read_only=True)
#     details = AssetDetailsSerializer(read_only=True)
#     columns = AssetColumnSerializer(many=True, read_only=True)
#
#     # Для создания/обновления по ID
#     type_id = serializers.PrimaryKeyRelatedField(
#         queryset=AssetType.objects.all(), source='type', write_only=True
#     )
#     domain_id = serializers.PrimaryKeyRelatedField(
#         queryset=AssetDomain.objects.all(), source='domain', write_only=True
#     )
#     details_id = serializers.PrimaryKeyRelatedField(
#         queryset=AssetDetails.objects.all(), source='details', write_only=True
#     )
#
#     class Meta:
#         model = Asset
#         fields = [
#             'id', 'type', 'domain', 'details', 'version', 'res_url', 'description',
#             'created_at', 'updated_at', 'is_active',
#             'type_id', 'domain_id', 'details_id',
#             'columns'
#         ]
