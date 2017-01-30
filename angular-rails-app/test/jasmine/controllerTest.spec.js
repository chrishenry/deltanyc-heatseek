describe('RegExp', function(){
  it('should match', function(){
    expect('string').toMatch(new RegExp('^dog$'));
  })
});