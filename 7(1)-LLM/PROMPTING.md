1. Direct Prompting, CoT Prompting, My Prompting을 0 shot, 3 shot, 5 shot 정답률을 표로 보여주세요!
| Model | 0-shot | 3-shot | 5-shot |
| :--- | :---: | :---: | :---: |
| **Direct Prompting** | 0.84 | 0.80 | 0.80 |
| **CoT Prompting** | 0.64 | 0.70 | 0.74 |
| **My Prompting** | 0.80 | 0.86 | 0.82 |


2. CoT Prompting이 Direct Prompting에 비해 왜 좋을 수 있는지에 대해서 서술해주세요!
실험 결과, Direct Prompting은 예시가 늘어날수록(0-shot 0.84 → 3-shot 0.80) 오히려 성능이 정체되거나 하락하는 경향을 보였습니다. 이는 모델이 중간 과정을 생략하고 '답만 맞히는 요령'을 과적합(Overfitting)했기 때문으로 보입니다. 반면 CoT Prompting은 0-shot(0.64)에서 시작해 5-shot(0.74)까지 예시가 늘어날수록 성능이 꾸준히 향상되었습니다.

GSM8K와 같은 복잡한 수학 문제에서 CoT는 거대한 문제를 작은 논리 단위로 쪼개어 해결하게 합니다. 비록 이번 실험에서는 Llama-3의 강력한 기본 성능 덕분에 Direct 0-shot 점수가 높았지만, 데이터가 많아질수록 모델에게 '논리적으로 추론하는 법'을 가르치는 CoT 방식이 더 안정적인 학습 곡선을 그린다는 것을 확인할 수 있었습니다.

3. 본인이 작성한 프롬프트 기법이 CoT에 비해 왜 더 좋을 수 있는지에 대해서 설명해주세요!
실험 결과, 제가 설계한 My Prompting은 3-shot에서 0.86(86%)의 가장 높은 정확도를 기록하며 Direct와 일반 CoT를 모두 앞섰습니다. 기존 CoT 대비 성능을 극대화할 수 있었던 이유는 다음 세 가지 전략 때문입니다.

첫째, 전문적인 페르소나와 검증 지시 (Expert Persona & Verification) 단순히 "생각해라"라고만 하는 CoT와 달리, 모델에게 "Expert Mathematician(전문 수학자)"라는 역할을 부여하여 더 신중하고 논리적인 어휘를 선택하도록 유도했습니다. 또한, 프롬프트에 "Double-check your calculations(계산을 재검토하라)"는 지시를 명시하여, CoT 과정에서 발생할 수 있는 단순 연산 실수를 스스로 줄이도록 안전장치를 마련했습니다.

둘째, 명확한 태그 분리 (Explicit Reasoning Tags) 일반적인 CoT는 줄글로 길게 답변하여 논리와 정답의 경계가 모호할 때가 있습니다. 저는 Few-shot 예시를 구성할 때 Reasoning:과 Answer: 태그를 명확히 분리하여 모델에게 학습시켰습니다. 이를 통해 모델은 "여기까지는 생각하는 구간이고, 여기부터는 정답 구간이다"라는 구조를 명확히 인식하게 되어 추론의 질이 향상되었습니다.

셋째, 파싱 최적화 (Parsing Optimization) 채점 프로그램이 정답을 인식하지 못해 오답 처리되는 것을 막기 위해 You MUST end your response with... "Answer: #### [Number]"라는 강력한 포맷 제약 조건을 걸었습니다. 그 결과, 모델이 정답을 맞히고도 형식 때문에 틀리는 경우를 획기적으로 줄일 수 있었고, 이것이 3-shot에서 86%라는 고득점을 달성한 핵심 요인이 되었습니다.