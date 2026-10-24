# S01E01 01:00–01:30 | model word-time comparison

**Research QA only.** Two model clocks agreeing does not prove the
original source dialogue has been heard or identify any character.
Wav2Vec2/CTC used approximate tiny.en speech segments as analysis windows.

Both models produced candidates for **39** original source words.
**37** start times agree within 300ms; **2** differ by more than 300ms.
Median signed CTC minus tiny.en start delta: **-37 ms**.

| Review category | Source word count |
|---|---:|
| CTC only model word candidate | 3 |
| no usable word timing candidate | 7 |
| tiny en only word candidate | 6 |
| two model start disagreement over 300ms | 2 |
| two model start proximity 300ms or less | 37 |

## High-priority source-word checks

The entries below lack a two-model start-time candidate within 300ms.
They require listening and/or an independent forced alignment; they
must not be automatically overwritten in the original captions.

- C0019 T1 word 1 (`DID`): no usable word timing candidate
- C0019 T1 word 2 (`YOU`): no usable word timing candidate
- C0019 T1 word 3 (`SAY`): no usable word timing candidate
- C0019 T1 word 4 (`MERCURIAL`): no usable word timing candidate
- C0019 T2 word 4 (`MAKE`): CTC only model word candidate
- C0022 T1 word 1 (`MY`): tiny en only word candidate
- C0022 T1 word 2 (`HOW`): two model start disagreement over 300ms
- C0022 T2 word 1 (`MINIMIFIDIAN`): no usable word timing candidate
- C0024 T1 word 1 (`DOES`): CTC only model word candidate
- C0024 T1 word 4 (`EXTRAVASATE`): CTC only model word candidate
- C0025 T1 word 1 (`WHAT`): two model start disagreement over 300ms
- C0026 T1 word 1 (`NO`): tiny en only word candidate
- C0027 T1 word 1 (`TELL`): tiny en only word candidate
- C0027 T1 word 2 (`THE`): tiny en only word candidate
- C0027 T1 word 3 (`JUDGE`): tiny en only word candidate
- C0027 T1 word 4 (`THE`): no usable word timing candidate
- C0027 T1 word 5 (`MAYOR`): tiny en only word candidate
- C0027 T1 word 6 (`CALLED`): no usable word timing candidate

## Acceptance limits

Most shared candidates land near one another because the original
caption sequence is plausible and the models use related source-audio
windows, **not** because timing was independently human verified.
Never infer speaker identity, emotional tone, a confirmed word correction
or transcript completeness from these statistics.
