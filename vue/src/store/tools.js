import Vue from 'vue';
import Vuex from 'vuex';
import i18n from '@/plugins/i18n';
import router from '@/router';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger.js';
import { displayErrorNotification } from '@/helpers/notifications';
import { asTool, asVersion } from '@/helpers/casl';

Vue.use( Vuex );

export const mutations = {
	TOOLS_LIST( state, tools ) {
		state.toolsList = asTool( tools.results );
		state.numTools = tools.count;
	},
	TOOL( state, tool ) {
		state.tool = asTool( tool );
	},
	SPDX_LICENSES( state, data ) {
		state.spdxLicenses = data;
	},
	CREATE_TOOL( state, tool ) {
		state.toolCreated = asTool( tool );
	},
	TOOL_REVISIONS( state, revisions ) {
		state.toolRevisions = asVersion( revisions.results );
		state.numRevisions = revisions.count;
	},
	TOOL_REVISION( state, revision ) {
		state.toolRevision = asVersion( revision );
	},
	DIFF_REVISION( state, revision ) {
		state.diffRevision = revision;
	}
};

export const actions = {
	listAllTools( context, page ) {
		const request = {
			url: '/api/tools/?page_size=12&page=' + page,
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'TOOLS_LIST', data );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},

	/**
	 * Fetch information for a single tool from the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {string} name - tool name
	 * @return {Promise<undefined>}
	 */
	getToolByName( context, name ) {
		const request = {
			url: '/api/tools/' + encodeURI( name ) + '/'
		};

		return makeApiCall( context, request ).then(
			( response ) => {
				context.commit( 'TOOL', response.body );
			},
			( failure ) => {
				const data = getFailurePayload( failure );
				if ( data.status_code === 404 ) {
					this._vm.$notify.warning(
						i18n.t( 'tool-not-found', [ name ] )
					);
				} else {
					displayErrorNotification.call( this, failure );
				}
			}
		);
	},
	getSpdxLicenses( context ) {
		const request = {
			url: '/api/spdx/?deprecated=false',
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'SPDX_LICENSES', data );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	createTool( context, toolInfo ) {
		const request = {
			url: '/api/tools/',
			method: 'POST',
			body: JSON.stringify( toolInfo )
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'CREATE_TOOL', data );
				router.push( {
					name: 'tools-view',
					params: { name: data.name }
				} );

				this._vm.$notify.success(
					i18n.t(
						'addremovetools-toolcreationsuccess',
						[ data.name ]
					),
					30000
				);
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	editTool( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/',
			method: 'PUT',
			body: JSON.stringify( tool.info )
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				router.push( {
					name: 'tools-view',
					params: { name: data.name }
				} );

				this._vm.$notify.success(
					i18n.t( 'tooleditingsuccess', [ data.name ] ), 30000
				);
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Update tool revisions state with the results obtained via the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 * @return {Promise<undefined>}
	 */
	updateToolRevisions( context, tool ) {
		return context.dispatch( 'getRevisions', tool ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'TOOL_REVISIONS', data );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Fetch tool revisions via the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 * @return {Promise} Promise object with revisions data
	 */
	getRevisions( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/?page=' + tool.page
		};
		return makeApiCall( context, request );
	},
	/**
	 * Fetch tool revision information from the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 * @return {Promise<undefined>}
	 */
	getToolRevision( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.revId + '/'
		};

		return makeApiCall( context, request ).then(
			( response ) => {
				context.commit( 'TOOL_REVISION', response.body );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Fetch differences between revisions from the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 * @return {Promise<undefined>}
	 */
	getToolRevisionsDiff( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.revId + '/diff/' + tool.otherId + '/'
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'DIFF_REVISION', data );
			},
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Undo changes between two revisions via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} payload
	 * @param {string} payload.name - tool name
	 * @param {number} payload.revId - starting revision id
	 * @param {number} payload.prevRevId - ending revision id
	 * @return {Promise<undefined>|undefined}
	 */
	undoChangesBetweenRevisions( context, { name, revId, prevRevId } ) {
		if ( !( !!revId && !!prevRevId ) ) {
			return;
		}

		const request = {
			url: '/api/tools/' + encodeURI( name ) + '/revisions/' + revId + '/undo/' + prevRevId + '/',
			method: 'POST'
		};

		return makeApiCall( context, request ).catch(
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Restore tool to a particular revision via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 * @return {Promise<undefined>}
	 */
	restoreToolToRevision( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.revId + '/revert/',
			method: 'POST'
		};

		return makeApiCall( context, request ).catch(
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Hide or reveal a particular revision via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 * @return {Promise<undefined>}
	 */
	hideRevealRevision( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.revId + '/' + tool.action + '/',
			method: 'PATCH'
		};

		return makeApiCall( context, request ).catch(
			( failure ) => {
				displayErrorNotification.call( this, failure );
			}
		);
	},
	/**
	 * Mark a revision as patrolled via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 * @return {Promise<undefined>}
	 */
	markRevisionAsPatrolled( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.revId + '/patrol/',
			method: 'PATCH'
		};

		return makeApiCall( context, request ).catch(
			( failure ) => {
				const data = getFailurePayload( failure );
				if ( data.code === 4093 ) {
					// T301870: treat already marked as patrolled error as
					// success and return
					return;
				} else {
					displayErrorNotification.call( this, failure );
				}
			}
		);
	}
};

export default {
	namespaced: true,
	state: {
		toolsList: [],
		tool: null,
		numTools: 0,
		spdxLicenses: [],
		toolCreated: {},
		toolRevisions: [],
		toolRevision: null,
		numRevisions: 0,
		diffRevision: null
	},
	actions,
	mutations,
	/* In strict mode, whenever Vuex state is mutated
	outside of mutation handlers, an error will be
	thrown. This ensures that all state mutations can
    be explicitly tracked by debugging tools.
	Disable strict mode in production to avoid the
    performance cost. */
	strict: process.env.NODE_ENV !== 'production'
};
