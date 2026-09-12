const display = document.getElementById('display');

function appendValue(val) {
    display.value += val;
}

function clearDisplay() {
    display.value = '';
}

function deleteLast() {
    display.value = display.value.slice(0, -1);
}

async function calculateResult() {
    if (!display.value.trim()) return;

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'expression',
                expression: display.value
            })
        });

        const data = await response.json();

        if (response.ok && data.result !== undefined) {
            display.value = data.result;
        } 
        else {
            display.value = data.error || 'Ошибка';
        }
    } 
    catch (err) {
        display.value = 'Ошибка сети';
    }
}

async function calcTrig(func) {
    const val = parseFloat(display.value);
    if (isNaN(val)) {
        display.value = 'Введите число';
        return;
    }

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                type: 'trig',
                func: func,
                value: val
            })
        });

        const data = await response.json();

        if (response.ok && data.result !== undefined) {
            display.value = data.result;
        } 
        else {
            display.value = data.error || 'Ошибка';
        }
    } 
    catch (err) {
        display.value = 'Ошибка сети';
    }
}