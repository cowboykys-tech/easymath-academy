import unittest
from unittest.mock import patch

from connectors import kakao_bridge


class KakaoBridgeContractTest(unittest.TestCase):
    def test_room_and_message_payloads_accept_common_driver_shapes(self):
        with patch.object(
            kakao_bridge,
            "driver_json",
            return_value={"chats": [{"chat_id": "room-1", "title": "검증방"}]},
        ):
            self.assertEqual(
                kakao_bridge.rooms_payload(),
                [{"chat_id": "room-1", "title": "검증방"}],
            )
        with patch.object(
            kakao_bridge,
            "driver_json",
            return_value={"messages": [{"author": "보호자", "text": "확인했습니다."}]},
        ):
            self.assertEqual(
                kakao_bridge.messages_payload("room-1", 20)[0]["text"],
                "확인했습니다.",
            )


if __name__ == "__main__":
    unittest.main()
