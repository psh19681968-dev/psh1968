(function () {
    const tabs = document.querySelectorAll('.tab');
    const input = document.getElementById('user-input');
    const label = document.getElementById('input-label');
    const examples = document.getElementById('examples');
    const generateBtn = document.getElementById('generate-btn');
    const btnText = generateBtn.querySelector('.btn-text');
    const outputSection = document.getElementById('output-section');
    const sermonOutput = document.getElementById('sermon-output');
    const statusEl = document.getElementById('status');
    const copyBtn = document.getElementById('copy-btn');
    const downloadBtn = document.getElementById('download-btn');
    const usageInfo = document.getElementById('usage-info');

    let currentType = 'topic';
    let accumulatedText = '';

    const EXAMPLES = {
        topic: [
            { label: '고난 속 평안', value: '고난 가운데 누리는 평안' },
            { label: '기다림의 믿음', value: '하나님의 때를 기다리는 믿음' },
            { label: '용서와 회복', value: '관계의 회복과 용서' },
            { label: '일상의 예배', value: '일상 속 예배' }
        ],
        passage: [
            { label: '시편 23편', value: '시편 23편' },
            { label: '마 11:28-30', value: '마태복음 11장 28-30절' },
            { label: '빌 4:6-7', value: '빌립보서 4장 6-7절' },
            { label: '롬 8:28', value: '로마서 8장 28절' }
        ]
    };

    function setType(type) {
        currentType = type;
        tabs.forEach(t => t.classList.toggle('active', t.dataset.type === type));

        if (type === 'topic') {
            label.textContent = '주제를 입력하세요';
            input.placeholder = '예) 고난 가운데 누리는 평안';
        } else {
            label.textContent = '성경 본문을 입력하세요';
            input.placeholder = '예) 시편 23편, 마태복음 11장 28-30절';
        }

        examples.innerHTML = '<span class="example-label">예시 :</span>';
        EXAMPLES[type].forEach(ex => {
            const btn = document.createElement('button');
            btn.className = 'example-chip';
            btn.textContent = ex.label;
            btn.dataset.value = ex.value;
            btn.addEventListener('click', () => {
                input.value = ex.value;
                input.focus();
            });
            examples.appendChild(btn);
        });
    }

    tabs.forEach(tab => {
        tab.addEventListener('click', () => setType(tab.dataset.type));
    });

    document.querySelectorAll('.example-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            input.value = chip.dataset.value;
            input.focus();
        });
    });

    function renderMarkdown(text) {
        const escaped = text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
        return escaped.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    }

    function setStatus(text, mode = '') {
        statusEl.textContent = text;
        statusEl.className = 'status' + (mode ? ' ' + mode : '');
    }

    function setLoading(loading) {
        generateBtn.disabled = loading;
        generateBtn.classList.toggle('loading', loading);
        btnText.textContent = loading ? '작성 중...' : '설교문 작성 시작';
        input.disabled = loading;
    }

    async function generateSermon() {
        const text = input.value.trim();
        if (!text) {
            input.focus();
            return;
        }

        accumulatedText = '';
        sermonOutput.innerHTML = '';
        usageInfo.classList.add('hidden');
        outputSection.classList.remove('hidden');
        copyBtn.disabled = true;
        downloadBtn.disabled = true;
        setStatus('준비하는 중...', 'thinking');
        setLoading(true);

        outputSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ input: text, type: currentType })
            });

            if (!response.ok) {
                const err = await response.json().catch(() => ({}));
                throw new Error(err.error || '서버 오류가 발생했습니다.');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder('utf-8');
            let buffer = '';
            let thinkingSeen = false;
            let writingStarted = false;

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    const raw = line.slice(6);
                    if (!raw) continue;

                    let event;
                    try {
                        event = JSON.parse(raw);
                    } catch (e) {
                        continue;
                    }

                    if (event.type === 'thinking') {
                        if (!thinkingSeen) {
                            setStatus('말씀을 묵상하는 중...', 'thinking');
                            thinkingSeen = true;
                        }
                    } else if (event.type === 'text') {
                        if (!writingStarted) {
                            setStatus('설교문을 기록하는 중...', 'thinking');
                            writingStarted = true;
                        }
                        accumulatedText += event.text;
                        sermonOutput.innerHTML = renderMarkdown(accumulatedText);
                    } else if (event.type === 'done') {
                        setStatus('완료 · 주님께 영광');
                        copyBtn.disabled = false;
                        downloadBtn.disabled = false;
                        if (event.usage) {
                            const u = event.usage;
                            const cached = u.cache_read_input_tokens || 0;
                            usageInfo.textContent =
                                `입력 토큰: ${u.input_tokens} · 출력 토큰: ${u.output_tokens}` +
                                (cached > 0 ? ` · 캐시 재사용: ${cached}` : '');
                            usageInfo.classList.remove('hidden');
                        }
                    } else if (event.type === 'error') {
                        throw new Error(event.message);
                    }
                }
            }
        } catch (err) {
            setStatus('오류');
            sermonOutput.innerHTML =
                `<div class="error-message">오류: ${err.message}</div>` + sermonOutput.innerHTML;
        } finally {
            setLoading(false);
        }
    }

    generateBtn.addEventListener('click', generateSermon);

    input.addEventListener('keydown', (e) => {
        if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
            e.preventDefault();
            generateSermon();
        }
    });

    copyBtn.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(accumulatedText);
            const prev = copyBtn.textContent;
            copyBtn.textContent = '복사됨';
            setTimeout(() => { copyBtn.textContent = prev; }, 1500);
        } catch (e) {
            alert('복사에 실패했습니다.');
        }
    });

    downloadBtn.addEventListener('click', () => {
        const blob = new Blob([accumulatedText], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        const date = new Date().toISOString().split('T')[0];
        a.href = url;
        a.download = `설교문_${date}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    setType('topic');
})();
