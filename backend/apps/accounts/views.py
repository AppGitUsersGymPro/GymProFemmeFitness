from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import CustomTokenObtainPairSerializer, UserSerializer, ChangePasswordSerializer
import logging
from apps.staff.models import StaffAttendance
from apps.members.models import MemberAttendance
from apps.devices.models import FingerprintSlot
from rest_framework import generics, status, permissions
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.http import HttpResponse

logger = logging.getLogger(__name__)
class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        try:
            response = super().post(request, *args, **kwargs)
        except Exception:
            logger.warning(f"[Login] Failed login attempt for username: {username}")
            raise
        logger.info(f"[Login] Successful login for username: {username}")
        return response

class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    def get_object(self):
        return self.request.user

class ChangePasswordView(APIView):
    def post(self, request):
        s = ChangePasswordSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(s.validated_data["old_password"]):
            logger.warning(f"[ChangePassword] Wrong old password supplied for user id={user.id}")
            return Response({"detail":"Wrong password"}, status=400)
        user.set_password(s.validated_data["new_password"])
        user.save()
        logger.info(f"[ChangePassword] Password changed successfully for user id={user.id}")
        return Response({"detail":"Password changed"})

class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def get_permissions(self):
        return [permissions.IsAdminUser()]

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"[UserCreate] New user created: id={user.id} username={user.username} role={user.role}")

@csrf_exempt
def iclock_data(request):
    if request.method == "GET":
        from django.utils import timezone
        return HttpResponse(
            f"GET OPTION FROM: {request.GET.get('SN', '')}\n"
            f"ATTLOGStamp=9999\n"
            f"OPERLOGStamp=9999\n"
            f"ATTPHOTOStamp=9999\n"
            f"ErrorDelay=30\n"
            f"Delay=30\n"
            f"TransTimes=00:00;14:05\n"
            f"TransInterval=1\n"
            f"TransFlag=TransData AttLog\n"
            f"TimeZone=5.5\n"
            f"Realtime=1\n"
            f"Encrypt=None\n"
        )

    if request.method == "POST":
        raw   = request.body.decode("utf-8", errors="ignore").strip()
        table = request.GET.get("table", "").strip()

        if table != "ATTLOG":
            return HttpResponse("OK")

        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue

            user_id    = parts[0].strip()   # e.g. "M0001" or "S0002"
            check_time = parts[1].strip()

            try:
                dt_obj = datetime.strptime(check_time, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue

            today      = dt_obj.date()
            punch_time = dt_obj.time()
            logger.warning(f"[Biometric] Raw user_id: {user_id} Time: {dt_obj}")

            # ── Resolve device user_id -> FingerprintSlot ──
            try:
                slot_id = int(user_id)
            except ValueError:
                logger.warning(f"[Biometric] Non-numeric user_id from device: {user_id}")
                continue

            try:
                slot = FingerprintSlot.objects.select_related("member", "staff").get(slot_id=slot_id)
            except FingerprintSlot.DoesNotExist:
                logger.warning(f"[Biometric] No FingerprintSlot found for slot_id={slot_id}")
                continue

            if slot.member_id:
                # ── Member ────────────────────────────────
                member = slot.member
                attendance, _ = MemberAttendance.objects.get_or_create(
                    member=member, date=today
                )
                if not attendance.check_in:
                    attendance.check_in = punch_time
                    punch_type = "IN"
                else:
                    attendance.check_out = punch_time
                    punch_type = "OUT"
                attendance.save()
                logger.info(f"[Member {punch_type}] {member.name} | {punch_time}")

            elif slot.staff_id:
                # ── Staff ─────────────────────────────────
                staff = slot.staff
                attendance, _ = StaffAttendance.objects.get_or_create(
                    staff=staff, date=today
                )
                if not attendance.check_in:
                    attendance.check_in = punch_time
                    punch_type = "IN"
                else:
                    attendance.check_out = punch_time
                    punch_type = "OUT"
                attendance.save()
                logger.info(f"[Staff {punch_type}] {staff.name} | {punch_time}")

            else:
                logger.warning(f"[Biometric] FingerprintSlot {slot_id} has neither member nor staff set")

        return HttpResponse("OK")

    return HttpResponse("FAILED")

@csrf_exempt
def iclock_getrequest(request):
    return HttpResponse("OK")
