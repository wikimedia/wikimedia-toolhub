import Vue from 'vue';
import Vuex from 'vuex';
import { makeApiCall, getFailurePayload } from '@/plugins/swagger.js';
import i18n from '@/plugins/i18n';

Vue.use( Vuex );

export const actions = {
	listAllUserGroups( context, page ) {
		const request = {
			url: '/api/groups/?page=' + page,
			method: 'GET'
		};

		return makeApiCall( context, request ).then(
			( success ) => {
				context.commit( 'GROUPS', success.body );
			},
			( failure ) => {
				const data = getFailurePayload( failure );

				this._vm.$notify.error(
					i18n.t( 'apierror', [ data ] )
				);
			}
		);
	},
	addMemberToGroup( context, payload ) {
		const request = {
			url: '/api/groups/' + payload.group.id + '/members/' + payload.member.id + '/',
			method: 'PUT'
		};

		return makeApiCall( context, request ).then(
			() => {
				const users = JSON.parse( JSON.stringify( context.rootState.user.users ) );

				const index = users.findIndex( ( user ) => user.id === payload.member.id );
				users[ index ].groups.push( payload.group );

				context.commit( 'user/USERS', { results: users, count: users.length }, { root: true } );

				context.commit( 'NOTIFICATION', {
					message: i18n.t( 'members-groupadd-success', [ payload.member.username, payload.group.name ] ),
					type: 'success'
				} );
			},
			( failure ) => {
				const data = getFailurePayload( failure );

				context.commit( 'NOTIFICATION', {
					message: i18n.t( 'apierror', [ data.message ] ),
					type: 'error'
				} );
			}
		);
	},
	removeMemberFromGroup( context, payload ) {
		const request = {
			url: '/api/groups/' + payload.group.id + '/members/' + payload.member.id + '/',
			method: 'DELETE'
		};

		return makeApiCall( context, request ).then(
			() => {
				const users = JSON.parse( JSON.stringify( context.rootState.user.users ) );

				const index = users.findIndex( ( user ) => user.id === payload.member.id );
				users[ index ].groups = users[ index ].groups.filter( ( group ) => {
					return group.id !== payload.group.id;
				} );

				context.commit( 'user/USERS', { results: users, count: users.length }, { root: true } );

				context.commit( 'NOTIFICATION', {
					message: i18n.t( 'members-groupremove-success', [ payload.member.username, payload.group.name ] ),
					type: 'success'
				} );
			},
			( failure ) => {
				const data = getFailurePayload( failure );

				context.commit( 'NOTIFICATION', {
					message: i18n.t( 'apierror', [ data.message ] ),
					type: 'error'
				} );
			}
		);
	}
};

export const mutations = {
	GROUPS( state, groups ) {
		state.groups = groups.results;
		state.numGroups = groups.count;
	},
	NOTIFICATION( state, data ) {
		state.notification = data;
	}
};

export default {
	namespaced: true,
	state: {
		groups: [],
		numGroups: 0,
		notification: null
	},
	actions: actions,
	mutations: mutations,
	// Strict mode in development/testing, but disabled for performance in prod
	strict: process.env.NODE_ENV !== 'production'
};
