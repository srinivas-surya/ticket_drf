from rest_framework import mixins, viewsets, exceptions

from .models import Event, TicketType, Order, DeleteOrderData
from .serializers import EventSerializer, TicketTypeSerializer, OrderSerializer
from rest_framework import generics

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from rest_framework import status
import datetime


class EventViewSet(generics.ListCreateAPIView):
    queryset = Event.objects.all().order_by("-id")
    serializer_class = EventSerializer


class OrderViewSet(mixins.CreateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        order = serializer.save(user=self.request.user)
        order.book_tickets()
        '''if not order.fulfilled:
            order.delete()
            raise exceptions.ValidationError("Couldn't book tickets")'''


class OrderDeletelApiView(APIView):

    def get_object(self, pk):
        order = get_object_or_404(Order, pk=pk)
        return order

    def delete(self, request, pk):
        order_detail = self.get_object(pk)
        date_now = datetime.datetime.now()
        order_created_date = str(order_detail.date)

        order_created = datetime.datetime(int(order_created_date[0:4]), int(order_created_date[5:7]),
                                          int(order_created_date[8:10]), int(order_created_date[11:13]),
                                          int(order_created_date[14:16]), int(order_created_date[17:19]))
        # check the time to delete the order
        seconds = (date_now - order_created)

        minutes = (seconds.total_seconds() / 60)

        if minutes <= 30.0:

            data = DeleteOrderData(ticket_type_id=order_detail.ticket_type_id,
                                   quantity=order_detail.quantity,
                                   order_id=order_detail.id)
            data.save()
            order_detail.delete()

            return Response("order deleted successfully", status=status.HTTP_204_NO_CONTENT)

        else:
            return Response("we cant delete order", status=status.HTTP_400_BAD_REQUEST)


class MetricDetailApiView(APIView):

    def get_object(self, pk):
        try:
            ticket_data = TicketType.objects.filter(event_id=pk)
            return ticket_data
        except ticket_data.DoesNotExist:
            return "None"

    def get(self, request, pk):
        data = self.get_object(pk)

        if len(data) == 0:
            return Response("No data found", status=status.HTTP_204_NO_CONTENT)
        else:
            live_order_data = Order.objects.filter(ticket_type_id=str(data[0].id))
            delete_order_data = DeleteOrderData.objects.filter(ticket_type_id=str(data[0].id))

            total_orders = (len(live_order_data)) + (len(delete_order_data))

            len_deleted_data = len(delete_order_data)
            len_live_data = len(live_order_data)

            cancellation_rate = ((len_deleted_data/total_orders)*100)

            response_data = {
                "Total_orders" : total_orders,
                "Active_orders": len_live_data,
                "Deleted_orders": len_deleted_data,
                "Cancellation_rate": cancellation_rate

            }

            return Response(response_data, status=status.HTTP_200_OK)






