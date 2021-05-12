'use strict';
import chai from 'chai';
import sinon from 'sinon';
import SwaggerClient from 'swagger-client';
import { addRequestDefaults } from '@/plugins/swagger';

chai.use( require( 'sinon-chai' ) );
const expect = chai.expect;
/* eslint-disable no-unused-expressions */

import { asTool } from '@/helpers/casl';
import {
	actions,
	mutations
} from './tools';

describe( 'store/tools', () => {
	const shortToolResponse = {
		author: 'Srish',
		bugtracker_url: 'http://testtracker.com',
		comment: "Tool with title 'ToolTest' created",
		description: 'Cooltool',
		license: 'AFL-1.1',
		name: 'Hellotool',
		repository: 'http://testrepo.com',
		title: 'ToolTest',
		tool_type: 'gadget',
		url: 'http://testurl.com',
		user_docs_url: [ {
			language: 'en',
			url: 'http://testdocs.com'
		} ]
	};

	const toolResponse = {
		...shortToolResponse,
		api_url: null,
		available_ui_languages: Array( 0 ),
		bot_username: null,
		created_by: {
			id: 2,
			username: 'Srish'
		},
		created_date: '2021-04-14T02:11:44.751235Z',
		deprecated: false,
		developer_docs_url: Array( 0 ),
		experimental: false,
		feedback_url: Array( 0 ),
		for_wikis: Array( 0 ),
		icon: null,
		keywords: Array( 0 ),
		modified_by: {
			id: 2,
			username: 'Srish'
		},
		modified_date: '2021-04-14T02:11:54.980904Z',
		openhub_id: null,
		origin: 'api',
		privacy_policy_url: Array( 0 ),
		replaced_by: null,
		sponsor: Array( 0 ),
		subtitle: null,
		technology_used: Array( 0 ),
		translate_url: null,
		url_alternates: [ {
			language: 'en',
			url: 'http://test123.com'
		} ],
		_language: 'en',
		_schema: null
	};

	const toolsListResponse = {
		count: 1,
		results: [
			toolResponse
		]
	};

	const spdxLicensesResponse = [
		{
			deprecated: false,
			fsf_approved: false,
			id: '0BSD',
			name: 'BSD Zero Clause License',
			osi_approved: true
		}
	];

	const toolRevisionResponse1 = {
		comment: 'This is a test edit',
		id: 596,
		timestamp: '2021-04-28T20:12:08.025365Z',
		user: {
			id: 2,
			username: 'Srish'
		}
	};

	const toolRevisionResponse2 = {
		comment: 'This is a test edit!!',
		id: 598,
		timestamp: '2021-04-27T20:12:08.025365Z',
		user: {
			id: 2,
			username: 'Srish'
		}
	};

	const toolRevisionsResponse = {
		count: 1,
		results: [
			toolRevisionResponse1,
			toolRevisionResponse2
		]
	};

	const diffRevisionResponse = {
		original: {
			id: 593,
			timestamp: '2021-04-28T19:49:31.735437Z',
			user: {
				id: 2,
				username: 'Srish'
			},
			comment: 'Test comment'
		},
		operations: [
			{
				op: 'replace',
				path: '/description',
				value: 'Cool tool it is'
			},
			{
				op: 'replace',
				path: '/repository',
				value: 'http://testrepo.co'
			}
		],
		result: {
			id: 596,
			timestamp: '2021-04-28T20:12:08.025365Z',
			user: {
				id: 2,
				username: 'Srish'
			},
			comment: 'Another test comment'
		}
	};

	describe( 'actions', () => {
		const commit = sinon.spy();
		const dispatch = sinon.stub();
		const state = { user: { is_authenticated: true } };
		const rootState = {
			locale: { locale: 'en' },
			user: { user: { csrf_token: 'abcd' } }
		};
		const context = { commit, dispatch, state, rootState };
		const stubThis = {
			_vm: {
				$notify: {
					error: sinon.stub(),
					success: sinon.stub()
				}

			}
		};

		let http = 'func';

		beforeEach( () => {
			http = sinon.stub( SwaggerClient, 'http' );
		} );
		afterEach( () => {
			http.restore();
			sinon.reset();
		} );

		describe( 'listAllTools', () => {
			const testPage = 2;
			const response = {
				ok: true,
				status: 200,
				url: '/api/tools/?page_size=12&page=' + testPage,
				headers: { 'Content-type': 'application/json' },
				body: toolsListResponse
			};

			it( 'should fetch tools', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/tools/?page_size=12&page=' + testPage
				}, context );
				http.resolves( response );

				await actions.listAllTools( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'TOOLS_LIST', toolsListResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const listAllTools = actions.listAllTools.bind( stubThis );
				await listAllTools( context, testPage );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );

		} );

		describe( 'getToolByName', () => {
			const testName = 'Awesome';
			const response = {
				ok: true,
				status: 200,
				url: '/api/tools/' + encodeURI( testName ),
				headers: { 'Content-type': 'application/json' },
				body: toolResponse
			};

			it( 'should fetch tool by name', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/tools/' + encodeURI( testName )
				}, context );
				http.resolves( response );

				await actions.getToolByName( context, testName );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'TOOL', toolResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const getToolByName = actions.getToolByName.bind( stubThis );
				await getToolByName( context, testName );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );

		} );

		describe( 'getSpdxLicenses', () => {
			const response = {
				ok: true,
				status: 200,
				url: '/api/spdx/',
				headers: { 'Content-type': 'application/json' },
				body: spdxLicensesResponse
			};

			it( 'should fetch spdx licenses', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/spdx/'
				}, context );
				http.resolves( response );

				await actions.getSpdxLicenses( context );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'SPDX_LICENSES', spdxLicensesResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const getSpdxLicenses = actions.getSpdxLicenses.bind( stubThis );
				await getSpdxLicenses( context );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );

		} );

		describe( 'createTool', () => {
			const response = {
				ok: true,
				status: 201,
				url: '/api/tools/',
				headers: { 'Content-type': 'application/json' },
				body: JSON.stringify( toolResponse )
			};

			it( 'should create tool', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/tools/',
					method: 'POST',
					body: JSON.stringify( shortToolResponse )
				}, context );
				http.resolves( response );

				await actions.createTool( context, shortToolResponse );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'CREATE_TOOL', JSON.stringify( toolResponse )
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { errors: [ {
					field: 'name',
					message: 'Tool with this title already exists'
				} ] } );

				const createTool = actions.createTool.bind( stubThis );
				await createTool( context, shortToolResponse );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );

		} );

		describe( 'editTool', () => {
			const testTool = {
				info: JSON.stringify( toolResponse ),
				name: 'Hellotool'
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/tools/' + testTool.name + '/',
				headers: { 'Content-type': 'application/json' },
				body: JSON.stringify( toolResponse )
			};

			it( 'should edit tool', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/tools/' + testTool.name + '/',
					method: 'PUT',
					body: JSON.stringify( testTool.info )
				}, context );
				http.resolves( response );

				const editTool = actions.editTool.bind( stubThis );
				await editTool( context, testTool );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.success ).to.have.been.called;

			} );

			it( 'should log failures', async () => {
				http.rejects( { errors: [ {
					field: 'name',
					message: 'Tool with this title already exists'
				} ] } );

				const editTool = actions.editTool.bind( stubThis );
				await editTool( context, toolResponse );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );

		} );

		describe( 'updateToolRevisions', () => {
			const testTool = {
				name: 'Hellotool',
				page: 1
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/tools/' + testTool.name + '/revisions/?page=' + testTool.page,
				headers: { 'Content-type': 'application/json' },
				body: toolRevisionsResponse
			};

			it( 'should fetch and update tool revisions', async () => {
				dispatch.onFirstCall().returns( { then: sinon.stub().yields( response ) } );
				actions.updateToolRevisions( context, testTool );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledBefore( commit );
				expect( dispatch ).to.have.been.calledWithExactly(
					'getRevisions', testTool
				);

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'TOOL_REVISIONS', toolRevisionsResponse
				);
			} );

			it( 'should log failures', async () => {
				dispatch.onFirstCall().rejects( { response: { data: 'Boom' } } );

				const updateToolRevisions = actions.updateToolRevisions.bind( stubThis );
				await updateToolRevisions( context, testTool );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledBefore( commit );
				expect( dispatch ).to.have.been.calledWithExactly(
					'getRevisions', testTool
				);

				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.calledOnce;
			} );

		} );

		describe( 'getToolRevision', () => {
			const testTool = {
				name: 'Awesome',
				revId: 596
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/tools/' + testTool.name + '/revisions/' + testTool.revId + '/',
				headers: { 'Content-type': 'application/json' },
				body: toolRevisionResponse1
			};

			it( 'should fetch tool revision', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/tools/' + testTool.name + '/revisions/' + testTool.revId + '/'
				}, context );
				http.resolves( response );

				await actions.getToolRevision( context, testTool );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'TOOL_REVISION', toolRevisionResponse1
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const getToolRevision = actions.getToolRevision.bind( stubThis );
				await getToolRevision( context, testTool );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );

		} );

		describe( 'getRevisionsDiff', () => {
			const testTool = {
				name: 'Awesome',
				id: 593,
				otherId: 596
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/tools/' + testTool.name + '/revisions/' + testTool.id + '/diff/' + testTool.otherId + '/',
				headers: { 'Content-type': 'application/json' },
				body: diffRevisionResponse
			};

			it( 'should fetch diff between revisions', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/tools/' + testTool.name + '/revisions/' + testTool.id + '/diff/' + testTool.otherId + '/'
				}, context );
				http.resolves( response );

				await actions.getRevisionsDiff( context, testTool );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( commit ).to.have.been.calledOnce;
				expect( commit ).to.have.been.calledWithExactly(
					'DIFF_REVISION', diffRevisionResponse
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );
				const getRevisionsDiff = actions.getRevisionsDiff.bind( stubThis );
				await getRevisionsDiff( context, testTool );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );

		} );

		describe( 'undoChangesBetweenRevisions', () => {
			const testTool = {
				name: 'Hellotool',
				id: '596',
				page: 1
			};

			const id = testTool.id,
				toolRevisions = toolRevisionsResponse.results,
				revIndex = toolRevisions.findIndex( ( revision ) => revision.id === id ),
				nextIndex = parseInt( revIndex ) + 1;

			const otherId = toolRevisions[ nextIndex ] && toolRevisions[ nextIndex ].id;

			const response = {
				ok: true,
				status: 200,
				url: '/api/tools/' + testTool.name + '/revisions/' + testTool.id + '/undo/' + otherId + '/',
				headers: { 'Content-type': 'application/json' },
				body: toolResponse
			};

			it( 'should undo between revisions', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/tools/' + testTool.name + '/revisions/' + id + '/undo/' + otherId + '/',
					method: 'POST'
				}, context );

				http.resolves( response );

				context.state.toolRevisions = toolRevisionsResponse.results;
				await actions.undoChangesBetweenRevisions( context, testTool );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( dispatch );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledWithExactly(
					'updateToolRevisions', {
						page: testTool.page,
						name: testTool.name
					}
				);

				context.state.toolRevisions = [];
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );

				context.state.toolRevisions = toolRevisionsResponse.results;
				const undoChangesBetweenRevisions = actions.undoChangesBetweenRevisions
					.bind( stubThis );
				await undoChangesBetweenRevisions( context, testTool );

				expect( http ).to.have.been.calledOnce;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.calledOnce;

				context.state.toolRevisions = [];
			} );

		} );

		describe( 'restoreToolToRevision', () => {
			const testTool = {
				name: 'Hellotool',
				id: '596',
				page: 1
			};

			const response = {
				ok: true,
				status: 200,
				url: '/api/tools/' + testTool.name + '/revisions/' + testTool.id + '/revert/',
				headers: { 'Content-type': 'application/json' }
			};

			it( 'should restore tool to a revision', async () => {
				const expectRequest = addRequestDefaults( {
					url: '/api/tools/' + testTool.name + '/revisions/' + testTool.id + '/revert/',
					method: 'POST'
				}, context );
				http.resolves( response );

				const restoreToolToRevision = actions.restoreToolToRevision.bind( stubThis );
				await restoreToolToRevision( context, testTool );

				expect( http ).to.have.been.calledOnce;
				expect( http ).to.have.been.calledBefore( commit );
				expect( http ).to.have.been.calledWith( expectRequest );

				expect( dispatch ).to.have.been.calledOnce;
				expect( dispatch ).to.have.been.calledWithExactly(
					'updateToolRevisions', {
						page: testTool.page,
						name: testTool.name
					}
				);
			} );

			it( 'should log failures', async () => {
				http.rejects( { response: { data: 'Boom' } } );

				const restoreToolToRevision = actions.restoreToolToRevision.bind( stubThis );
				await restoreToolToRevision( context, testTool );

				expect( http ).to.have.been.calledOnce;
				expect( commit ).to.have.not.been.called;
				// eslint-disable-next-line no-underscore-dangle
				expect( stubThis._vm.$notify.error ).to.have.been.called;
			} );

		} );

	} );

	describe( 'mutations', () => {
		it( 'should store tool, tools list and tool created', () => {
			const state = {
				toolsList: [],
				numTools: 0,
				tool: null,
				toolCreated: {}
			};

			const tools = {
				results: toolsListResponse.results,
				count: toolsListResponse.count
			};

			mutations.TOOLS_LIST( state, tools );
			expect( state.toolsList ).to.eql( asTool( tools.results ) );
			expect( state.numTools ).to.equal( tools.count );

			mutations.TOOL( state, toolResponse );
			expect( state.tool ).to.eql( asTool( toolResponse ) );

			mutations.CREATE_TOOL( state, toolResponse );
			expect( state.toolCreated ).to.eql( asTool( toolResponse ) );
		} );

		it( 'should store licenses', () => {
			const state = {
				spdxLicenses: []
			};

			mutations.SPDX_LICENSES( state, spdxLicensesResponse );
			expect( state.spdxLicenses ).to.equal( spdxLicensesResponse );
		} );

		it( 'should store diff and tool revisions', () => {
			const state = {
				toolRevisions: [],
				numRevisions: 0,
				diffRevision: null,
				toolRevision: null
			};

			mutations.TOOL_REVISIONS( state, toolRevisionsResponse );
			expect( state.toolRevisions ).to.equal( toolRevisionsResponse.results );
			expect( state.numRevisions ).to.equal( toolRevisionsResponse.count );

			mutations.TOOL_REVISION( state, toolRevisionResponse1 );
			expect( state.toolRevision ).to.equal( toolRevisionResponse1 );

			mutations.DIFF_REVISION( state, diffRevisionResponse );
			expect( state.diffRevision ).to.equal( diffRevisionResponse );
		} );

	} );

} );
