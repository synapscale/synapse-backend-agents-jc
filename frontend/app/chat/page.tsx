"use client"

import React from 'react'
import { AppProvider } from '@/context/app-context'
import { OnboardingProvider } from '@/components/onboarding/onboarding-context'
import { ThemeProvider } from '@/components/theme/theme-provider'
import { KeyboardShortcutsProvider } from '@/components/keyboard-shortcuts/keyboard-shortcuts-context'
import { FeedbackProvider } from '@/components/chat/feedback-context'
import { AnalyticsProvider } from '@/lib/analytics-provider'
import ChatInterface from '@/components/chat/chat-interface'
import OnboardingTour from '@/components/onboarding/onboarding-tour'

export default function ChatPage() {
  return (
    <AnalyticsProvider pageId="chat">
      <AppProvider>
        <ThemeProvider>
          <KeyboardShortcutsProvider>
            <FeedbackProvider>
              <OnboardingProvider>
                <div className="h-screen flex flex-col">
                  <ChatInterface />
                  <OnboardingTour tourId="chat-tour" />
                </div>
              </OnboardingProvider>
            </FeedbackProvider>
          </KeyboardShortcutsProvider>
        </ThemeProvider>
      </AppProvider>
    </AnalyticsProvider>
  )
}
