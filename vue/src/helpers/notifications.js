import { getFailurePayload } from '@/plugins/swagger';
import i18n from '@/plugins/i18n';

/**
 * Display error notification of api call in a nice
 * format using notify plugin.
 *
 * @this caller method this.
 * @example displayErrorNotification.call(this, failure).
 * @param {Object} failure - api error response object.
 * @return {undefined}
 */
export function displayErrorNotification( failure ) {
	const data = getFailurePayload( failure );

	for ( const err in data.errors ) {
		this._vm.$notify.error(
			i18n.t( 'apierrors', [
				data.errors[ err ].field,
				data.errors[ err ].message
			] )
		);
	}
}
