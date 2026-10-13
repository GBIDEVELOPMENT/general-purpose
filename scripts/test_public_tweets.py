import unittest
from scripts.collect_public_tweets import parse_timeline, compact, ID


class NitterParserTests(unittest.TestCase):
    def test_timeline_and_cursor(self):
        markup = """
          <div class="timeline-item">
            <div class="tweet-header"><a class="username" href="/ianmakesjokes">@ianmakesjokes</a></div>
            <a class="tweet-link" href="/ianmakesjokes/status/1456789012345678901">time</a>
            <div class="tweet-content">Setup.<br>Then punchline.</div>
          </div>
          <div class="timeline-item">
            <div class="retweet-header">RT</div>
            <a class="tweet-link" href="/other/status/1456789012345678902">time</a>
            <div class="tweet-content">Someone else</div>
          </div>
          <div class="show-more"><a href="/ianmakesjokes?cursor=abc">Load more</a></div>
        """
        posts, cursor = parse_timeline(markup)
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]["id"], "1456789012345678901")
        self.assertEqual(posts[0]["author"], "ianmakesjokes")
        self.assertEqual(posts[0]["text"], "Setup. Then punchline.")
        self.assertTrue(posts[1]["is_repost"])
        self.assertEqual(cursor, "/ianmakesjokes?cursor=abc")

    def test_reply_and_unrelated_text(self):
        posts, _ = parse_timeline("""
          <div class="timeline-item">
            <div class="replying-to">Reply</div>
            <a href="/ianmakesjokes/status/1456789012345678901">post</a>
            <div class="tweet-content">A response</div>
          </div>
          <div class="random"><div class="tweet-content">Not a tweet</div></div>
        """)
        self.assertEqual(len(posts), 1)
        self.assertTrue(posts[0]["is_reply"])
        self.assertEqual(posts[0]["text"], "A response")

    def test_utils(self):
        self.assertEqual(compact("  a  b\nc "), "a b c")
        self.assertEqual(ID.search("/user/status/1456789012345678901?foo=bar").group(1),
                         "1456789012345678901")


if __name__ == "__main__":
    unittest.main()
