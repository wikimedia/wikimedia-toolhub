let globalIdCounter = Date.now();

export const getters = {};

export const actions = {
	/**
	 * Post a message.
	 *
	 * @param {Object} context - Vuex context
	 * @param {Object} payload
	 * @param {string|null} payload.message - content
	 * @param {string|null} payload.type - success, info, warning, error
	 * @param {boolean|null} payload.prominent - Draw more attention
	 * @param {number|null} payload.timeout - Dismiss after N milliseconds
	 * @return {number} Message id
	 */
	message( context, payload ) {
		const mid = globalIdCounter++;
		if ( payload.timeout ) {
			payload.timeout = window.setTimeout( () => {
				context.commit( 'onClearMessage', mid );
			}, Number( payload.timeout ) );
		}
		context.commit( 'onMessage', {
			id: mid,
			message: payload.message,
			type: payload.type,
			prominent: payload.prominent,
			timeoutID: payload.timeout || null
		} );
		return mid;
	},

	/**
	 * Announce a successful action.
	 *
	 * @param {Object} context - Vuex context
	 * @param {Object} payload
	 * @param {string} payload.message - Content
	 * @param {number|null} payload.timeout - Time in milliseconds to display
	 * @return {number} Message id
	 */
	success( context, payload ) {
		return context.dispatch( 'message', {
			message: payload.message,
			timeout: payload.timeout || null,
			type: 'success'
		} );
	},

	/**
	 * Present information to the user.
	 *
	 * @param {Object} context - Vuex context
	 * @param {Object} payload
	 * @param {string} payload.message - Content
	 * @param {number|null} payload.timeout - Time in milliseconds to display
	 * @return {number} Message id
	 */
	info( context, payload ) {
		return context.dispatch( 'message', {
			message: payload.message,
			timeout: payload.timeout || null,
			type: 'info'
		} );
	},

	/**
	 * Raise a warning.
	 *
	 * @param {Object} context - Vuex context
	 * @param {string} msg - Warning
	 * @return {number} Message id
	 */
	warning( context, msg ) {
		return context.dispatch( 'message', {
			message: msg,
			type: 'warning',
			prominent: true
		} );
	},

	/**
	 * Signal an error.
	 *
	 * @param {Object} context - Vuex context
	 * @param {string} msg - Error message
	 * @return {number} Message id
	 */
	error( context, msg ) {
		return context.dispatch( 'message', {
			message: msg,
			type: 'error',
			prominent: true
		} );
	},

	/**
	 * Remove a message.
	 *
	 * @param {Object} context - Vuex context
	 * @param {number} messageId - Message id
	 */
	clearMessage( context, messageId ) {
		context.commit( 'onClearMessage', messageId );
	}
};

export const mutations = {
	/**
	 * Persist a message.
	 *
	 * @param {Object} state - Vuex state tree.
	 * @param {Object} payload - mutation payload.
	 * @param {number} payload.id - message id
	 * @param {string|null} payload.message - content
	 * @param {string|null} payload.type - success, info, warning, error
	 * @param {boolean|null} payload.prominent - Draw more attention
	 * @param {number|null} payload.timeoutID - Active timer id
	 */
	onMessage( state, payload ) {
		if ( payload && payload.id ) {
			state.messages.push( {
				id: payload.id,
				message: payload.message,
				type: payload.type,
				prominent: payload.prominent,
				timeoutID: payload.timeoutID || false
			} );
		}
	},

	/**
	 * Remove a message.
	 *
	 * @param {Object} state - Vuex state tree.
	 * @param {number} messageId - Message id
	 */
	onClearMessage( state, messageId ) {
		if ( state.messages && state.messages.length ) {
			state.messages = state.messages.filter( ( item ) => {
				if ( item.id === messageId && item.timeoutID ) {
					window.clearTimeout( item.timeoutID );
				}
				return item.id !== messageId;
			} );
		}
	}
};

export default {
	namespaced: true,
	state: {
		messages: []
	},
	getters: getters,
	actions: actions,
	mutations: mutations,
	strict: process.env.NODE_ENV !== 'production'
};
