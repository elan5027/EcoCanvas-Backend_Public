from rest_framework import serializers
from users.models import User
from .models import User, password_validator, password_pattern
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class SignUpSerializer(serializers.ModelSerializer):
    '''
    작성자 : 이주한
    내용 : 회원가입에 필요한 Sign Up Serializer 클래스
    최초 작성일 : 2023.06.06
    업데이트 일자 : 2023.06.10
    '''
    re_password = serializers.CharField(
        error_messages={
            "required": "비밀번호 확인은 필수 입력 사항입니다!",
            "blank": "비밀번호 확인은 필수 입력 사항입니다!",
        }
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "re_password",
            "email",
        )
        extra_kwargs = {
            "email": {
                "error_messages": {
                    "required": "email은 필수 입력 사항입니다!",
                    "invalid": "email 형식이 맞지 않습니다. 알맞은 형식의 email을 입력해주세요!",
                    "blank": "email은 필수 입력 사항입니다!",
                }
            },
            "username": {
                "error_messages": {
                    "required": "이름은 필수 입력 사항입니다!",
                    "blank": "이름은 필수 입력 사항입니다!",
                }
            },
            "password": {
                "write_only": True,
                "error_messages": {
                    "required": "비밀번호는 필수 입력 사항입니다!",
                    "blank": "비밀번호는 필수 입력 사항입니다!",
                },
            },
        }

    def validate(self, data):
        password = data.get("password")
        re_password = data.get("re_password")

        if password != re_password:
            raise serializers.ValidationError(
                detail={"password": "비밀번호와 비밀번호 확인이 일치하지 않습니다!"})

        if password_validator(password):
            raise serializers.ValidationError(
                detail={"password": "비밀번호는 8자 이상의 영문 대소문자와 숫자, 특수문자를 포함하여야 합니다!"})

        if password_pattern(password):
            raise serializers.ValidationError(
                detail={"password": "비밀번호는 연속해서 3자리 이상 동일한 영문,숫자,특수문자 사용이 불가합니다!"})

        return data

    def create(self, validated_data):
        email = validated_data["email"]
        username = validated_data["username"]
        password = validated_data["password"]
        validated_data.pop("re_password", None)
        user = User.objects.create(username=username, email=email,)
        user.set_password(password)
        user.save()

        return validated_data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    '''
    작성자 : 이주한
    내용 : 로그인에 필요한 Custom Token Obtain Pair Serializer 클래스
    최초 작성일 : 2023.06.06
    업데이트 일자 :
    '''
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = user.id
        token["email"] = user.email
        token["is_admin"] = user.is_admin
        return token


class UserSerializer(serializers.ModelSerializer):
    '''
    작성자 : 박지홍
    내용 : 어드민 페이지에서 필요한 유저의 정보를 직렬화 하는 Serializer 클래스
    최초 작성일 : 2023.06.09
    업데이트 일자 :
    '''
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_active']