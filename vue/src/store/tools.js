import Vue from 'vue';
import Vuex from 'vuex';
import i18n from '@/plugins/i18n';
import router from '@/router';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger.js';
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

		makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'TOOLS_LIST', data );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},

	/**
	 * Fetch information for a single tool from the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {string} name - tool name
	 * @return {Promise}
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
					this._vm.$notify.error(
						i18n.t( 'apierror', [ data.message ] )
					);
				}
			}
		);
	},
	getSpdxLicenses( context ) {
		const request = {
			url: '/api/spdx/',
			method: 'GET',
			headers: {
				'Content-Type': 'application/json'
			}
		};

		makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'SPDX_LICENSES', data );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},
	createTool( context, toolInfo ) {
		const request = {
			url: '/api/tools/',
			method: 'POST',
			body: JSON.stringify( toolInfo )
		};

		makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'CREATE_TOOL', data );
				router.push( { path: '/tool/' + data.name } );

				this._vm.$notify.success(
					i18n.t( 'addremovetools-toolcreationsuccess', [ data.name ] ), 30000
				);
			},
			( failure ) => {
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
		);
	},
	editTool( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/',
			method: 'PUT',
			body: JSON.stringify( tool.info )
		};

		makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				router.push( { path: '/tool/' + data.name } );

				this._vm.$notify.success(
					i18n.t( 'tooleditingsuccess', [ data.name ] ), 30000
				);
			},
			( failure ) => {
				const data = getFailurePayload( failure );

				for ( const err in data.errors ) {
					this._vm.$notify.error(
						i18n.t( 'editformerror', [
							data.message,
							data.errors[ err ].field,
							data.errors[ err ].message
						] )
					);
				}
			}
		);
	},
	/**
	 * Update tool revisions state with the results obtained via the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 */
	updateToolRevisions( context, tool ) {
		context.dispatch( 'getRevisions', tool ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'TOOL_REVISIONS', data );
			},
			( failure ) => {
				const data = getFailurePayload( failure );

				this._vm.$notify.error(
					i18n.t( 'apierror', [ data ] )
				);
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
	 */
	getToolRevision( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.revId + '/'
		};

		makeApiCall( context, request ).then(
			( response ) => {
				context.commit( 'TOOL_REVISION', response.body );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},
	/**
	 * Fetch differences between revisions from the API.
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 */
	getRevisionsDiff( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.id + '/diff/' + tool.otherId + '/'
		};

		makeApiCall( context, request ).then(
			( success ) => {
				const data = success.body;
				context.commit( 'DIFF_REVISION', data );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},
	/**
	 * Undo changes between two revisions via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 */
	async undoChangesBetweenRevisions( context, tool ) {
		const id = tool.id,
			nextPage = tool.page + 1,
			toolRevisions = context.state.toolRevisions,
			revIndex = toolRevisions.findIndex( ( revision ) => revision.id === id ),
			nextIndex = parseInt( revIndex ) + 1;

		let otherId = '';

		if ( nextIndex === toolRevisions.length ) {
			// Fetch more revisions to obtain other id if the revision
			// selected for an undo is last in the current list
			await context.dispatch( 'getRevisions', {
				name: tool.name, page: nextPage
			} ).then(
				( success ) => {
					const results = success.body.results;
					otherId = results[ 0 ].id; // Get rev id from the first element
				},
				( failure ) => {
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
			);
		} else {
			otherId = toolRevisions[ nextIndex ] && toolRevisions[ nextIndex ].id;
		}

		if ( !( !!id && !!otherId ) ) {
			return;
		}

		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + id + '/undo/' + otherId + '/',
			method: 'POST'
		};

		makeApiCall( context, request ).then(
			() => {
				context.dispatch( 'updateToolRevisions', {
					page: tool.page,
					name: tool.name
				} );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},
	/**
	 * Restore tool to a particular revision via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 */
	restoreToolToRevision( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.id + '/revert/',
			method: 'POST'
		};

		makeApiCall( context, request ).then(
			() => {
				context.dispatch( 'updateToolRevisions', {
					page: tool.page,
					name: tool.name
				} );
			},
			( failure ) => {
				const explanation = ( 'statusCode' in failure ) ?
					failure.response.statusText : failure;

				this._vm.$notify.error(
					i18n.t( 'apierror', [ explanation ] )
				);
			}
		);
	},
	/**
	 * Hide or reveal a particular revision via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 */
	hideRevealRevision( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.id + '/' + tool.action + '/',
			method: 'PATCH'
		};

		makeApiCall( context, request ).then(
			() => {
				context.dispatch( 'updateToolRevisions', {
					page: tool.page,
					name: tool.name
				} );
			},
			( failure ) => {
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
		);
	},
	/**
	 * Mark a revision as patrolled via the API
	 *
	 * @param {Object} context - vuex context
	 * @param {Object} tool - tool info
	 */
	markRevisionAsPatrolled( context, tool ) {
		const request = {
			url: '/api/tools/' + encodeURI( tool.name ) + '/revisions/' + tool.id + '/patrol/',
			method: 'PATCH'
		};

		makeApiCall( context, request ).then(
			() => {
				context.dispatch( 'updateToolRevisions', {
					page: tool.page,
					name: tool.name
				} );
			},
			( failure ) => {
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
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
