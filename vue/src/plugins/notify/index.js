import module from './vuex';
import Notifications from './component';

export let $store;

export function setStore( store ) {
	$store = store;
}

export const methods = {
	/**
	 * Signal a successful action.
	 *
	 * @param {string} message - Content
	 * @param {number} [timeout=0] - Time in milliseconds to display
	 * @return {number} Message id
	 */
	success( message, timeout = 0 ) {
		return $store.dispatch( 'notify/success', { message, timeout } );
	},

	/**
	 * Present information to the user.
	 *
	 * @param {string} message - Content
	 * @param {number} [timeout=0] - Time in milliseconds to display
	 * @return {number} Message id
	 */
	info( message, timeout = 0 ) {
		return $store.dispatch( 'notify/info', { message, timeout } );
	},

	/**
	 * Raise a warning.
	 *
	 * @param {string} msg - Warning
	 * @return {number} Message id
	 */
	warning( msg ) {
		return $store.dispatch( 'notify/warning', msg );
	},

	/**
	 * Signal an error.
	 *
	 * @param {string} msg - Error message
	 * @return {number} Message id
	 */
	error( msg ) {
		return $store.dispatch( 'notify/error', msg );
	},

	/**
	 * Remove a notification.
	 *
	 * @param {number} messageId - Message id
	 * @return {undefined}
	 */
	clear( messageId ) {
		return $store.dispatch( 'notify/clearMessage', messageId );
	}
};

/**
 * Install this plugin.
 *
 * @param {Object} Vue - Vue instance installing plugin
 * @param {Object} options - Plugin options
 * @param {Object} options.store - Vuex store
 */
export function install( Vue, options ) {
	if ( install.installed ) {
		return;
	}
	if ( !options.store ) {
		throw new Error( 'Required options.store Vuex instance missing.' );
	}

	install.installed = true;
	setStore( options.store );

	options.store.registerModule( 'notify', module );
	Vue.component( 'Notifications', Notifications );
	Vue.prototype.$notify = methods;
}

export default {
	install
};
