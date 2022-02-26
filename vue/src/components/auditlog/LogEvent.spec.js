/* eslint-disable no-unused-expressions */
/* eslint-disable no-unused-vars */
'use strict';
import chai from 'chai';
import sinon from 'sinon';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;

import { shallowMount } from '@vue/test-utils';

import EventIcon from '@/components/auditlog/EventIcon';
import EventTimestamp from '@/components/auditlog/EventTimestamp';
import UserLink from '@/components/auditlog/UserLink';
import LogEvent from './LogEvent';

describe( 'components/auditlog', () => {
	describe( 'LogEvent', () => {
		const buildWrapper = function ( event ) {
			return shallowMount(
				LogEvent, {
					propsData: { log: event },
					computed: { isRTL: () => true }
				}
			);
		};

		const expectCommonStructure = function ( wrapper, event ) {
			expect( wrapper ).to.be.an( 'object' );
			expect( wrapper.classes() ).to.contain( 'log-event' );
			expect( wrapper.classes() ).to.contain( 'row' );

			const icon = wrapper.findComponent( EventIcon );
			expect( icon.exists() ).to.be.true;

			const timestamp = wrapper.findComponent( EventTimestamp );
			expect( timestamp.exists() ).to.be.true;

			if ( event.user !== null ) {
				const userlink = wrapper.findComponent( UserLink );
				expect( userlink.exists() ).to.be.true;
				expect( userlink.html() ).to.contain( event.user.username );
			}
		};

		it( 'tool-updated', () => {
			const event = {
				id: 1132,
				timestamp: '2021-06-11T23:04:46.956231Z',
				user: {
					id: 2,
					username: 'BDavis (WMF)'
				},
				target: {
					type: 'tool',
					id: 'test-20210514',
					label: 'test-20210514'
				},
				action: 'updated',
				params: {},
				message: '+developer_docs'
			};
			const wrapper = buildWrapper( event );

			expectCommonStructure( wrapper, event );

			const tools = wrapper.findAll( '.log-event-tool' );
			expect( tools.length ).to.equal( 1 );
			expect( tools.at( 0 ).html() ).to.contain( event.target.label );
		} );
		it( 'toollist-updated', () => {
			const event = {
				id: 9729,
				timestamp: '2022-02-24T16:10:27.282777Z',
				user: {
					id: 2,
					username: 'BDavis (WMF)'
				},
				target: {
					type: 'toollist',
					id: 20,
					label: 'foo'
				},
				action: 'updated',
				params: {},
				message: 'change title to create diff'
			};
			const wrapper = buildWrapper( event );

			expectCommonStructure( wrapper, event );

			const lists = wrapper.findAll( '.log-event-toollist' );
			expect( lists.length ).to.equal( 1 );
			expect( lists.at( 0 ).html() ).to.contain( event.target.label );
		} );
		it( 'url-created', () => {
			const event = {
				id: 9698,
				timestamp: '2022-02-15T01:07:59.939958Z',
				user: {
					id: 2,
					username: 'BDavis (WMF)'
				},
				target: {
					type: 'url',
					id: 150,
					label: 'https://example.org/'
				},
				action: 'created',
				params: {},
				message: null
			};
			const wrapper = buildWrapper( event );

			expectCommonStructure( wrapper, event );

			const urls = wrapper.findAll( '.log-event-url' );
			expect( urls.length ).to.equal( 1 );
			expect( urls.at( 0 ).html() ).to.contain( event.target.label );
		} );
		it( 'user-created', () => {
			const event = {
				id: 4367,
				timestamp: '2021-10-13T01:48:40.705503Z',
				user: null,
				target: {
					type: 'user',
					id: 4,
					label: 'Toolhub'
				},
				action: 'created',
				params: {},
				message: null
			};
			const wrapper = buildWrapper( event );

			expectCommonStructure( wrapper, event );
		} );
		it( 'group-added-to', () => {
			const event = {
				id: 9701,
				timestamp: '2022-02-15T23:47:01.608010Z',
				user: {
					id: 2,
					username: 'BDavis (WMF)'
				},
				target: {
					type: 'group',
					id: 1,
					label: 'Administrators'
				},
				action: 'added to',
				params: {
					user: {
						id: 2,
						username: 'BDavis (WMF)'
					}
				},
				message: null
			};
			const wrapper = buildWrapper( event );

			expectCommonStructure( wrapper, event );

			const groups = wrapper.findAll( '.log-event-group' );
			expect( groups.length ).to.equal( 1 );
			expect( groups.at( 0 ).html() ).to.contain( event.target.label );
		} );
		it( 'version-patrolled', () => {
			const event = {
				id: 9697,
				timestamp: '2022-02-14T03:12:25.268690Z',
				user: {
					id: 2,
					username: 'BDavis (WMF)'
				},
				target: {
					type: 'version',
					id: 3798,
					label: ''
				},
				action: 'patrolled',
				params: {
					tool_name: 'person-test-01'
				},
				message: null
			};
			const wrapper = buildWrapper( event );

			expectCommonStructure( wrapper, event );

			const revisions = wrapper.findAll( '.log-event-version' );
			expect( revisions.length ).to.equal( 1 );
			expect( revisions.at( 0 ).html() ).to.contain( event.target.id );

			const tools = wrapper.findAll( '.log-event-tool' );
			expect( tools.length ).to.equal( 1 );
			expect( tools.at( 0 ).html() ).to.contain( event.params.tool_name );
		} );
	} );
} );
