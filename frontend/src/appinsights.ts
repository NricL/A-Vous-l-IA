/**
 * Application Insights Telemetry Module (Avoulia V2)
 * RGPD-safe: no cookies, no persistent ID, no IP logging
 * Session ID regenerated weekly via localStorage
 */

export interface TelemetryEvent {
  name: string;
  properties?: Record<string, string | number>;
  measurements?: Record<string, number>;
}

class AppInsights {
  private instrumentationKey: string;
  private sessionId: string;
  private caseHash: string | null;
  private readonly STORAGE_KEY = 'ai_session_id';
  private readonly STORAGE_EXPIRY = 'ai_session_expiry';
  private readonly WEEKLY_MS = 7 * 24 * 60 * 60 * 1000;

  constructor(instrumentationKey: string) {
    this.instrumentationKey = instrumentationKey;
    this.sessionId = this.getOrCreateSessionId();
    this.caseHash = document.body.getAttribute('data-case-hash');
    this.initEventListeners();
  }

  private getOrCreateSessionId(): string {
    const now = Date.now();
    const stored = localStorage.getItem(this.STORAGE_KEY);
    const expiry = localStorage.getItem(this.STORAGE_EXPIRY);

    if (stored && expiry && now < parseInt(expiry)) {
      return stored;
    }

    // Create new session
    const sessionId = `sess_${Math.random().toString(36).substring(2, 15)}`;
    localStorage.setItem(this.STORAGE_KEY, sessionId);
    localStorage.setItem(this.STORAGE_EXPIRY, (now + this.WEEKLY_MS).toString());
    return sessionId;
  }

  private initEventListeners() {
    // Track step completion (checkboxes)
    document.addEventListener('change', (e) => {
      const target = e.target as HTMLInputElement;
      if (target?.closest?.('.coche input[type="checkbox"]')) {
        const stepEl = target.closest('[data-step-number]') as HTMLElement;
        if (stepEl) {
          const stepNum = stepEl.getAttribute('data-step-number');
          const stepName = stepEl.getAttribute('data-step-name') || `Étape ${stepNum}`;
          this.trackStepCompletion(parseInt(stepNum!), stepName, 0);
        }
      }
    });

    // Track quickwin accordion
    document.addEventListener('toggle', (e) => {
      const target = e.target as HTMLDetailsElement;
      if (target?.closest?.('.quickwin-accordion')) {
        const action = target.open ? 'open' : 'close';
        this.trackQuickwinAction(action);
      }
    });

    // Track copy button
    document.addEventListener('click', (e) => {
      const target = e.target as HTMLElement;
      if (target?.hasAttribute?.('data-copie')) {
        const text = target.textContent || '';
        this.trackQuickwinAction('copy', text);
      }
    });
  }

  /**
   * Track chat session start
   */
  trackChatSessionStart() {
    this.trackEvent({
      name: 'chat_session_start',
      properties: {
        sessionId: this.sessionId,
        timestamp: new Date().toISOString(),
        url: window.location.pathname,
      },
    });
  }

  /**
   * Track user message sent
   */
  trackUserMessage(messageText: string, questionCategory: string = 'unknown') {
    this.trackEvent({
      name: 'user_message_sent',
      properties: {
        sessionId: this.sessionId,
        messageLength: messageText.length,
        questionCategory,
        timestamp: new Date().toISOString(),
      },
      measurements: {
        characterCount: messageText.length,
      },
    });
  }

  /**
   * Track RAG result returned
   */
  trackRagResult(caseId: string, matchingScore: number, caseTitle: string = 'unknown') {
    this.trackEvent({
      name: 'rag_result_returned',
      properties: {
        sessionId: this.sessionId,
        caseId,
        matchingScore: matchingScore.toString(),
        caseTitle: caseTitle.substring(0, 50),
        timestamp: new Date().toISOString(),
      },
      measurements: {
        score: matchingScore,
      },
    });
  }

  /**
   * Track parcours URL proposed
   */
  trackParcoursUrlProposed(parcoursUrl: string, caseHash: string) {
    this.caseHash = caseHash;
    this.trackEvent({
      name: 'parcours_url_proposed',
      properties: {
        sessionId: this.sessionId,
        parcoursUrl,
        caseHash,
        timestamp: new Date().toISOString(),
      },
    });
  }

  /**
   * Track parcours page opened
   */
  trackParcoursPageOpened(caseHash?: string) {
    const hash = caseHash || this.caseHash || document.body.getAttribute('data-case-hash') || 'unknown';
    this.trackEvent({
      name: 'parcours_page_opened',
      properties: {
        sessionId: this.sessionId,
        caseHash: hash,
        timestamp: new Date().toISOString(),
        url: window.location.pathname,
      },
    });
  }

  /**
   * Track step completion (étape 1-6)
   */
  trackStepCompletion(stepNumber: number, stepName: string, completionTime: number = 0) {
    this.trackEvent({
      name: `parcours_step_${stepNumber}_completed`,
      properties: {
        sessionId: this.sessionId,
        caseHash: this.caseHash || 'unknown',
        stepNumber: stepNumber.toString(),
        stepName,
        timestamp: new Date().toISOString(),
      },
      measurements: {
        completionTimeSeconds: completionTime,
      },
    });
  }

  /**
   * Track quickwin action (open/close/copy)
   */
  trackQuickwinAction(action: 'open' | 'close' | 'copy', copiedText?: string) {
    this.trackEvent({
      name: `quickwin_${action}`,
      properties: {
        sessionId: this.sessionId,
        caseHash: this.caseHash || 'unknown',
        action,
        copiedTextLength: copiedText ? copiedText.length.toString() : '0',
        timestamp: new Date().toISOString(),
      },
    });
  }

  /**
   * Track validation step (étape 1)
   */
  trackValidation(q1: string, q2: string, q3: string) {
    this.trackEvent({
      name: 'parcours_validation_answers',
      properties: {
        sessionId: this.sessionId,
        caseHash: this.caseHash || 'unknown',
        q1,
        q2,
        q3,
        timestamp: new Date().toISOString(),
      },
    });
  }

  /**
   * Track session end
   */
  trackSessionEnd(completedSteps: number = 0) {
    this.trackEvent({
      name: 'chat_session_end',
      properties: {
        sessionId: this.sessionId,
        completedSteps: completedSteps.toString(),
        timestamp: new Date().toISOString(),
      },
      measurements: {
        stepCount: completedSteps,
      },
    });
  }

  /**
   * Internal: send event to App Insights
   */
  private trackEvent(event: TelemetryEvent) {
    if (!this.instrumentationKey) {
      console.warn('[Telemetry] No instrumentation key set');
      return;
    }

    const payload = {
      name: event.name,
      time: new Date().toISOString(),
      iKey: this.instrumentationKey,
      data: {
        baseType: 'EventData',
        baseData: {
          ver: 2,
          name: event.name,
          properties: event.properties || {},
          measurements: event.measurements || {},
        },
      },
    };

    // Send via sendBeacon (reliable, doesn't block)
    const url = 'https://dc.applicationinsights.azure.com/v2/track';
    navigator.sendBeacon(url, JSON.stringify([payload]));

    // Log locally for debugging
    console.log('[Telemetry]', event.name, event.properties);
  }

  /**
   * Get session ID (for debugging)
   */
  getSessionId(): string {
    return this.sessionId;
  }
}

// Singleton export
let instance: AppInsights | null = null;

export function initializeAppInsights(instrumentationKey: string): AppInsights {
  if (!instance) {
    instance = new AppInsights(instrumentationKey);
  }
  return instance;
}

export function getAppInsights(): AppInsights | null {
  return instance;
}
