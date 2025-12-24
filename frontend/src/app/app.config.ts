import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAuth0, authHttpInterceptorFn } from '@auth0/auth0-angular';

import { routes } from './app.routes';
import { environment } from '../environments/environment';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(
      withInterceptors([authHttpInterceptorFn])
    ),
    provideAuth0({
      domain: environment.auth0.domain,
      clientId: environment.auth0.clientId,
      authorizationParams: {
        redirect_uri: environment.auth0.redirectUri,
        audience: environment.auth0.audience
      },
      httpInterceptor: {
        allowedList: [
          {
            // Add token to all API calls - let backend decide if it's needed
            uri: `${environment.apiUrl}/*`,
            tokenOptions: {
              authorizationParams: {
                audience: environment.auth0.audience
              }
            },
            allowAnonymous: true
          }
        ]
      }
    })
  ]
};