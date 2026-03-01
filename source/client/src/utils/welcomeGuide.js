const WELCOME_GUIDE_KEY = 'fyp_welcome_guide_shown'

export function shouldShowWelcomeGuide() {
  return !localStorage.getItem(WELCOME_GUIDE_KEY)
}

export function markWelcomeGuideHidden(dontShowAgain) {
  if (dontShowAgain) {
    localStorage.setItem(WELCOME_GUIDE_KEY, 'true')
  }
}

export function scheduleWelcomeGuide(onShow, delay = 1000) {
  if (typeof onShow !== 'function') {
    return null
  }
  return setTimeout(() => {
    onShow()
  }, delay)
}

export function clearWelcomeGuideTimer(timerId) {
  if (!timerId) {
    return
  }
  clearTimeout(timerId)
}
