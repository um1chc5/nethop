"""Five-letter word bank (secrets and valid guesses)."""

WORDS = frozenset(
    w
    for w in """
    about after again alloy amber anode angle array atlas audio
    badge batch blade blink board brace brick cable cache cargo chase
    click clock cloud crane crash crate cyber crypt debug delta drain
    drift drone ember fault fiber field flash fleet float frame ghost
    glare globe grain graph growl guard hobby hover input ivory jolly
    knack laser latch layer light liver logic login lunar match metal
    micro modem motor night north notch ocean orbit patch panel phase
    pixel place plant plank probe pulse punch query queue radar radio
    range rapid ratio relay robot rogue rover scale scout scope score
    shaft shard shift sigma skate slice solid space spark stack steam
    steel stone storm super surge swarm swift table tapir torch trace
    track trail troop ultra vapor vault venom virus vivid vocal watch
    whale wired world wreck yacht zebra
    """.split()
    if len(w) == 5
)

assert all(len(w) == 5 for w in WORDS)
assert len(WORDS) >= 40
