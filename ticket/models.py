from django.db import models, transaction
from django.conf import settings


class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        db_table = "event"


class TicketType(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, related_name='ticket_types', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, editable=False)

    class Meta:
        db_table = "ticket_type"

    def available_tickets(self):
        return self.tickets.filter(order__isnull=True)

    def save(self, *args, **kwargs):
        new = not self.pk
        super().save(*args, **kwargs)
        if new:
            self.tickets.bulk_create([Ticket(ticket_type=self)] * self.quantity)


class Ticket(models.Model):
    ticket_type = models.ForeignKey(TicketType, related_name='tickets', on_delete=models.CASCADE)
    order = models.ForeignKey('ticket.Order', related_name='tickets',
                              default=None, null=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "ticket"


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.PROTECT)
    ticket_type = models.ForeignKey(TicketType, related_name='orders', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    fulfilled = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ticket_order"

    def book_tickets(self):
        if self.fulfilled:
            raise Exception('Order already fulfilled')
        qs = self.ticket_type.available_tickets().select_for_update(skip_locked=True)[:self.quantity]
        try:
            with transaction.atomic():
                updated_count = self.ticket_type.tickets.filter(id__in=qs).update(order=self)
                if updated_count != self.quantity:
                    raise Exception
        except Exception:
            return
        self.fulfilled = True
        self.save(update_fields=['fulfilled'])


class DeleteOrderData(models.Model):
    ticket_type_id = models.PositiveIntegerField()
    quantity = models.PositiveIntegerField()
    order_id = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "delete_order_data"

