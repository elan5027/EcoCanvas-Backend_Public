from rest_framework.generics import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ShopProduct, ShopCategory, ShopOrder, ShopOrderDetail
from .serializers import (
    ProductListSerializer, CategoryListSerializer, OrderProductSerializer, OrderDetailSerializer
)
from config.permissions import IsAdminUserOrReadonly
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 60


class ProductListViewAPI(APIView):
    '''
    작성자:장소은
    내용: 전체 상품 목록 쿼리 매개변수 통해 조건별 정렬 조회 API
    작성일: 2023.06.16
    '''
    pagination_class = CustomPagination

    def get(self, request):
        sort_by = request.GET.get('sort_by')
        if sort_by == 'hits':
            products = ShopProduct.objects.all().order_by('-hits')
        elif sort_by == 'high_price':
            products = ShopProduct.objects.all().order_by('-product_price')
        elif sort_by == 'low_price':
            products = ShopProduct.objects.all().order_by('product_price')
        else:
            products = ShopProduct.objects.all().order_by('-product_date')
        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)


class ProductCategoryListViewAPI(APIView):
    '''
    작성자:장소은
    내용: 카테고리별 상품목록 조회(조회순/높은금액/낮은금액/최신순) (일반,관리자) / 상품 등록(관리자) 
    작성일: 2023.06.06
    업데이트일: 2023.06.16
    '''
    permission_classes = [IsAdminUserOrReadonly]
    pagination_class = CustomPagination

    def get(self, request, category_id):
        category = get_object_or_404(ShopCategory, id=category_id)

        sort_by = request.GET.get('sort_by')
        if sort_by == 'hits':
            products = ShopProduct.objects.filter(
                category_id=category.id).order_by('-hits')
        elif sort_by == 'high_price':
            products = ShopProduct.objects.filter(
                category_id=category.id).order_by('-product_price')
        elif sort_by == 'low_price':
            products = ShopProduct.objects.filter(
                category_id=category.id).order_by('product_price')
        else:
            products = ShopProduct.objects.filter(
                category_id=category.id).order_by('-product_date')

        paginator = self.pagination_class()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductListSerializer(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)

    def post(self, request, category_id):
        category = get_object_or_404(ShopCategory, id=category_id)
        serializer = ProductListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(category=category)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailViewAPI(APIView):
    '''
    작성자:장소은
    내용: 카테고리별 상품 상세 조회/ 수정 / 삭제 (일반유저는 조회만) 
          +) 조회수 기능 추가
    작성일: 2023.06.06
    업데이트일: 2023.06.15
    '''
    permission_classes = [IsAdminUserOrReadonly]

    def get(self, request, product_id):
        product = get_object_or_404(ShopProduct, id=product_id)
        serializer = ProductListSerializer(product)
        product.hits += 1
        product.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, product_id):
        product = get_object_or_404(ShopProduct, id=product_id)
        serializer = ProductListSerializer(
            product, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        product = get_object_or_404(ShopProduct, id=product_id)
        product.delete()
        return Response({"massage": "삭제 완료"}, status=status.HTTP_204_NO_CONTENT)


class AdminProductViewAPI(APIView):
    '''
    작성자 : 박지홍
    내용 : 어드민 페이지에서 전체 상품 목록을 받아오기위해 사용
    최초 작성일 : 2023.06.09
    업데이트 일자 :
    '''

    def get(self, request):
        products = ShopProduct.objects.all().order_by('-product_date')
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminCategoryViewAPI(APIView):
    '''
    작성자 : 박지홍, 장소은
    내용 : 어드민 페이지에서 전체 카테고리 목록을 받아오기 및 카테고리 생성하기 위해 사용
    최초 작성일 : 2023.06.09, 2023.06.12
    업데이트 일자 :
    '''

    def get(self, request):
        categorys = ShopCategory.objects.all()
        serializer = CategoryListSerializer(categorys, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CategoryListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderProductViewAPI(APIView):
    '''
    작성자 : 장소은
    내용 : 해당 상품에 대한 주문 생성 / 사용자가 proudct_id에 해당하는 상품 목록 조회 
    최초 작성일 : 2023.06.13
    업데이트 일자 :
    '''

    def get(self, request, product_id):
        orders = ShopOrder.objects.filter(
            user=request.user.id, product_id=product_id)
        serializer = OrderProductSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, product_id):
        product = get_object_or_404(ShopProduct, id=product_id)
        serializer = OrderProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(product=product)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminOrderViewAPI(APIView):
    '''
    작성자 : 장소은
    내용 : 어드민 페이지에서 해당 상품에 대한 모든 주문내역 조회
    최초 작성일 : 2023.06.09
    업데이트 일자 :
    '''

    def get(self, request, product_id):
        orders = ShopOrder.objects.filter(product_id=product_id)
        serializer = OrderProductSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MypageOrderViewAPI(APIView):
    '''
    작성자 : 장소은
    내용 : 마이페이지에서 유저의 모든 주문내역 조회
    최초 작성일 : 2023.06.14
    업데이트 일자 :
    '''

    def get(self, request):
        orders = ShopOrder.objects.filter(user=request.user.id)
        serializer = OrderProductSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
