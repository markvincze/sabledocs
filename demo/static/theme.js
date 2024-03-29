
const storageKey = 'theme-preference'

const onClick = () => {
    // flip current value
    theme.value = theme.value === 'light'
        ? 'dark'
        : 'light'

    setPreference()
}

const getColorPreference = () => {
    if (localStorage.getItem(storageKey))
        return localStorage.getItem(storageKey)
    else
        return window.matchMedia('(prefers-color-scheme: dark)').matches
            ? 'dark'
            : 'light'
}

const setPreference = () => {
    localStorage.setItem(storageKey, theme.value)
    reflectPreference()
}

const reflectPreference = () => {
    const body = document.querySelector('body');
    const html = document.querySelector('html'); // The html element is also configured to make sure the background color is correct on mobile if the content overflows horizontally.

    if (theme.value === 'dark') {
        body.className = 'dark';
        html.className = 'dark';
    } else {
        body.className = '';
        html.className = '';
    }

    document.firstElementChild
        .setAttribute('data-theme', theme.value)

    document
        .querySelector('#theme-toggle')
        ?.setAttribute('aria-label', theme.value)
}

const theme = {
    value: getColorPreference(),
}

window.addEventListener(
    "load",
    () => {
        // set on load so screen readers can see latest value on the button
        reflectPreference()

        // now this script can find and listen for clicks on the control
        document
            .querySelector('#theme-toggle')
            .addEventListener('click', onClick)
    });

// sync with system changes
window
    .matchMedia('(prefers-color-scheme: dark)')
    .addEventListener('change', ({matches:isDark}) => {
        theme.value = isDark ? 'dark' : 'light'
        setPreference()
    });
