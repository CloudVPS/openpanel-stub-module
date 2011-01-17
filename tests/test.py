from OpenPanel.exception import CoreException

def testcreate(ctx):
    stub = ctx.prefix+'stub1.example.com'
    stubs = ctx.conn.rpc.getrecords(classid="Stub")
    if stub in stubs['body']['data'].get('Stub',{}).keys():
        ctx.fail("stubcreate-already-exists", "found Stub %s before create" % stub)
        return False
    success = False
    try:
        ctx.conn.rpc.create(classid="Stub", objectid=stub, data=dict(cmd='failnow.example.net'))['body']['data']['objid']
    except CoreException:
        success = True
    if not success:
        ctx.fail("stubcreate-failnow-create", "Stub module ignored failnow trigger")
        return
        
    ctx.logger.debug("failnow-create of stub %s correctly refused" % (stub))

    success = True
    try:
        stubid = ctx.conn.rpc.create(classid="Stub", objectid=stub, data=dict(cmd='failnot.example.net'))['body']['data']['objid']
    except CoreException:
        success = False
        ctx.fail("stubcreate-failnot-create", "failnow-create has blocked failnot-create")
        
    if success:
        ctx.logger.debug("failnot-create of stub %s succeeded (%s)" % (stub, stubid))

    success = True
    try:
        ctx.conn.rpc.delete(classid="Stub", objectid=stub)
    except CoreException:
        success = False
        ctx.fail("stubcreate-delete", "stub delete failed")
        
    if success:
        ctx.logger.debug("stub %s deleted" % (stub))

    return True

def testupdate(ctx):
    stub = ctx.prefix+'stub2.example.com'
    stubs = ctx.conn.rpc.getrecords(classid="Stub")
    if stub in stubs['body']['data'].get('Stub',{}).keys():
        ctx.fail("stubupdate-already-exists", "found Stub %s before create" % stub)
        return False
    try:
        stubid = ctx.conn.rpc.create(classid="Stub", objectid=stub, data=dict(cmd='failnot.example.net'))['body']['data']['objid']
    except CoreException, ex:
        ctx.fail("stubupdate-failnot-create", "Stub module failnot create failed")
        return

    ctx.logger.debug("failnot-create of stub %s succeeded" % (stub))

    success = False
    try:
        ctx.conn.rpc.update(classid="Stub", objectid=stubid, data=dict(cmd='failnow.example.net'))['body']['data']['objid']
    except CoreException:
        success = True

    if not success:
        ctx.fail("stubupdate-failnow-update", "failnow-update incorrectly allowed")

    if success:
        ctx.logger.debug("failnow-update of stub %s correctly refused (%s)" % (stub, stubid))

    gone = False
    stubs = ctx.conn.rpc.getrecords(classid="Stub")
    if stub not in stubs['body']['data'].get('Stub',{}).keys():
        gone = True
        ctx.fail("stubupdate-gone", "Stub %s gone after failnow update" % stub)
        
    success = True
    try:
        ctx.conn.rpc.delete(classid="Stub", objectid=stub)
    except CoreException:
        success = False

    ### FIXME
    if not success and not gone:
        ctx.fail("stubupdate-delete", "stub %s delete failed" % (stub))

    if success and gone:
        ctx.fail("stubupdate-delete-ghost", "stub %s deleted even though it was already gone" % (stub))

    if success and not gone:
        ctx.logger.debug("delete of stub %s succeeded" % stub)
    
    if not success and gone:
        ctx.logger.debug("delete failed on already-gone %s stub, that's okay" % (stub))

    return True

def test(ctx):
    testcreate(ctx)
    testupdate(ctx)

def cleanup(ctx):
    return True
