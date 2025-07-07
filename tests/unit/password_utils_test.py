from app.utils.password import hash_password, verify_password


class TestPasswordUtils:
    """Test cases for password utilities"""

    def test_hash_password(self):
        """Test password hashing"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password  # Should be different from original
        assert len(hashed) > 0

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "test_password_123"
        hashed = hash_password(password)

        result = verify_password(password, hashed)
        assert result is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "test_password_123"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        result = verify_password(wrong_password, hashed)
        assert result is False

    def test_hash_password_special_characters(self):
        """Test password hashing with special characters"""
        password = "test@#$%^&*()_+-=[]{}|;':\",./<>?"
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True

    def test_hash_password_unicode(self):
        """Test password hashing with unicode characters"""
        password = "test_пароль_密码_パスワード"
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        password = "TestPassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True
        assert verify_password(password.lower(), hashed) is False
        assert verify_password(password.upper(), hashed) is False
