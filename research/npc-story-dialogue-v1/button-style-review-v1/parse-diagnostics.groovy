def s=new File(args[0]);['build-interface.groovy','diagnostic-no-styles.groovy','diagnostic-no-native.groovy','diagnostic-block.groovy'].each{n->
 try{new GroovyClassLoader().parseClass(new File(s,n));println n+' PARSE OK'}catch(Throwable e){println n+' '+e.message}
}
